import re
import codewave_core.logger as logger
	
class StrPos():
	def __init__(self,pos,str):
		self.pos,self.str = pos,str
	def end(self) :
		self.pos + len(self.str)

class Pos(object):
	def __init__(self,start,end = None):
		if end is None :
			end = start
		self.start,self.end = start,end
		self.initVars()
	def initVars(self):
		self._editor = None
		self._prevEOL = self._nextEOL = self._textWithFullLines = self._sameLinesPrefix = self._sameLinesSuffix = None
	def containsPt(self,pt):
		return self.start <= pt and pt <= self.end
	def containsPos(self,pos):
		return self.start <= pos.start and pos.end <= self.end
	def wrappedBy(self,prefix,suffix):
		return WrappedPos(self.start - len(prefix), self.start, self.end, self.end + len(suffix))
	def withEditor(self,val):
		self._editor = val
		return self
	def editor(self):
		if self._editor is None:
			raise NameError('No editor set')
		return self._editor
	def hasEditor(self):
		return self._editor is not None
	def text(self):
		return self.editor().textSubstr(self.start, self.end)
	def applyOffset(self,offset):
		if offset != 0:
			self.start += offset
			self.end += offset
		return self
	def prevEOL(self):
		if self._prevEOL is None:
			self._prevEOL = self.editor().findLineStart(self.start)
		return self._prevEOL
	def nextEOL(self):
		if self._nextEOL is None:
			self._nextEOL = self.editor().findLineEnd(self.end)
		return self._nextEOL
	def textWithFullLines(self):
		if self._textWithFullLines is None:
			self._textWithFullLines = self.editor().textSubstr(self.prevEOL(),self.nextEOL())
		return self._textWithFullLines
	def sameLinesPrefix(self):
		if self._sameLinesPrefix is None:
			self._sameLinesPrefix = self.editor().textSubstr(self.prevEOL(),self.start)
		return self._sameLinesPrefix
	def sameLinesSuffix(self):
		if self._sameLinesSuffix is None:
			self._sameLinesSuffix = self.editor().textSubstr(self.end,self.nextEOL())
		return self._sameLinesSuffix
	def copy(self):
		res = Pos(self.start,self.end)
		if self.hasEditor():
			res.withEditor(self.editor())
		return res
	def raw(self):
		return [self.start,self.end]
		
class WrappedPos(Pos):
	def __init__(self, start,innerStart,innerEnd,end):
		self.start,self.innerStart,self.innerEnd,self.end = start,innerStart,innerEnd,end
		self.initVars()
	def innerContainsPt(self,pt):
		return self.innerStart <= pt and pt <= self.innerEnd
	def innerContainsPos(self,pos):
		return self.innerStart <= pos.start and pos.end <= self.innerEnd
	def innerText(self):
		return self.editor().textSubstr(self.innerStart, self.innerEnd)
	def setInnerLen(self,len):
		self.moveSufix(self.innerStart + len)
	def moveSuffix(self,pt):
		suffixLen = self.end - self.innerEnd
		self.innerEnd = pt
		self.end = self.innerEnd + suffixLen
	def copy(self):
		return WrappedPos(self.start,self.innerStart,self.innerEnd,self.end)

class Size():
	def __init__(self, width,height):
		self.width,self.height = width,height

class OptionObject():
	def setOpts(self,options,defaults):
		self.defaults = defaults
		for key, val in self.defaults.items():
			if key in options:
				self.setOpt(key,options[key])
			else:
				self.setOpt(key,val)
				
	def setOpt(self,key, val):
		setattr(self,key,val)
				
	def getOpt(self,key):
		return getattr(self,key)
	
	def getOpts(self):
		opts = {}
		for key, val in self.defaults.items():
			opts[key] = self.getOpt(key)
		return opts
		
class Replacement(Pos, OptionObject):
	def __init__(self, start, end, text, options = {}):
		self.start, self.end, self.text, self.options = start, end, text, options
		self.setOpts(self.options)
		self.initVars()
	def setOpts(self,options):
		super(Replacement, self).setOpts(options,{
			'prefix': '',
			'suffix': '',
			'selections': []
		})
	def resPosBeforePrefix(self):
		return self.start+len(self.prefix)+len(self.text)
	def resEnd(self): 
		return self.start+len(self.finalText())
	def apply(self):
		self.editor().spliceText(self.start, self.end, self.finalText())
	def necessary(self):
		return self.finalText() != self.originalText()
	def originalText(self):
		return self.editor().textSubstr(self.start, self.end)
	def finalText(self):
		return self.prefix+self.text+self.suffix
	def offsetAfter(self): 
		return len(self.finalText()) - (self.end - self.start)
	def applyOffset(self,offset):
		if offset != 0:
			self.start += offset
			self.end += offset
			for sel in self.selections:
				sel.start += offset
				sel.end += offset
		return self
	def selectContent(self): 
		self.selections = [Pos(len(self.prefix)+self.start, len(self.prefix)+self.start+len(self.text))]
		return self
	def carretToSel(self):
		self.selections = []
		text = self.finalText()
		self.prefix = removeCarret(self.prefix)
		self.text = removeCarret(self.text)
		self.suffix = removeCarret(self.suffix)
		start = self.start
		
		while True :
			res = getAndRemoveFirstCarret(text)
			if res is None:
				break
			pos,text = res
			self.selections.append(Pos(start+pos, start+pos))
			
		return self
	def copy(self): 
		res = Replacement(self.start, self.end, self.text, self.getOpts())
		if self.hasEditor():
			res.withEditor(self.editor())		
		res.selections = list(map(lambda s: s.copy(), self.selections))
		return res
		
class Wrapping(Replacement):
	def __init__(self, start, end, prefix ='', suffix = '', options = {}):
		self.start, self.end, self.options = start, end, options
		self.setOpts(self.options)
		self.text = ''
		self.prefix = prefix
		self.suffix = suffix
		self.initVars()
	def apply(self):
		self.adjustSel()
		super(self.__class__, self).apply()
	def adjustSel(self):
		offset = len(self.originalText())
		for sel in self.selections:
			if sel.start > self.start+len(self.prefix):
				sel.start += offset
			if sel.end >= self.start+len(self.prefix):
				sel.end += offset
	def finalText(self):
		if self.hasEditor():
			text = self.originalText()
		else:
			text = ''
		return self.prefix+text+self.suffix
	def offsetAfter(self): 
		return len(self.prefix)+len(self.suffix)
					
	def copy(self): 
		res = Wrapping(self.start, self.end, self.prefix, self.suffix)
		res.selections = list(map(lambda s: s.copy(), self.selections))
		return res
		

class PairMatch():
	def __init__(self, pair,match,offset = 0):
		self.pair,self.match,self.offset = pair,match,offset
		self._name = None
	def name(self):
		if self.match:
			if self._name is None:
				for i, group in enumerate(self.match.groups()):
					if group is not None:
						return self.pair.matchAnyPartKeys()[i]
				_name = False
			return _name or None
	def start(self):
		return self.match.start() + self.offset
	def end(self):
		return self.match.end() + self.offset
	def valid(self):
		return not self.pair.validMatch or self.pair.validMatch(self)
	def length(self):
		return len(self.match.group(0))
		
class Pair():
	def __init__(self, opener,closer,options = {}):
		self.opener,self.closer,self.options = opener,closer,options
		defaults = {
			'optionnal_end': False,
			'validMatch': None
		}
		for key, val in defaults.items():
			if key in self.options:
				setattr(self,key,self.options[key])
			else:
				setattr(self,key,val)
	def openerReg(self):
		if isinstance(self.opener, str) :
			return re.compile(escapeRegExp(self.opener))
		else:
			return self.opener
	def closerReg(self):
		if isinstance(self.closer, str) :
			return re.compile(escapeRegExp(self.closer))
		else:
			return self.closer
	def matchAnyParts(self):
		return {
			'opener' : self.openerReg(),
			'closer' : self.closerReg()
		}
	def matchAnyPartKeys(self):
		keys = []
		for key, reg in self.matchAnyParts().items():
			keys.append(key)
		return keys
	def matchAnyReg(self):
		groups = []
		for key, reg in self.matchAnyParts().items():
			groups.append('('+reg.pattern+')')
		return re.compile('|'.join(groups))
	def matchAny(self,text,offset=0):
		while True:
			match = self._matchAny(text,offset)
			if match is None or match.valid():
				break
			offset = match.end()
		if match is not None and match.valid():
			return match 
	def _matchAny(self,text,offset=0):
		if offset:
			text = text[offset:]
		match = re.search(self.matchAnyReg(),text)
		if match is not None:
			return PairMatch(self,match,offset)
	def matchAnyNamed(self,text):
		return self._matchAnyGetName(self.matchAny(text))
	def matchAnyLast(self,text,offset=0):
		res = None
		while True:
			match = self.matchAny(text,offset)
			if match is None:
				break
			offset = match.end()
			if res is None or res.end() != match.end():
				res = match
		return res
	def identical(self):
		return self.opener == self.closer
	def wrapperPos(self,pos,text):
		start = self.matchAnyLast(text[0:pos.start])
		if start is not None and (self.identical() or start.name() == 'opener'):
			end = self.matchAny(text,pos.end)
			if end is not None and (self.identical() or end.name() == 'closer'):
				return Pos(start.start(),end.end())
			elif self.optionnal_end:
				return Pos(start.start(),len(text))
	def isWapperOf(self,pos,text):
		return self.wrapperPos(pos,text) is not None
		

def splitFirstNamespace(fullname,isSpace = False) :
	if not ":" in fullname and not isSpace:
		return [None,fullname]
	parts = fullname.split(':')
	return [parts.pop(0), ':'.join(parts) or None]

def splitNamespace(fullname) :
	if ":" not in fullname:
		return [None,fullname]
	parts = fullname.split(':')
	name = parts.pop()
	return [':'.join(parts),name]

def trimEmptyLine(txt) :
	return re.sub(r'^\s*\r?\n', '', re.sub(r'\r?\n\s*$', '', txt))

def escapeRegExp(txt) :
	return re.escape(txt)

def repeatToLength(txt, length):
	return (txt * (int(length/len(txt))+1))[:length]

def repeat(txt, nb):
	return txt * nb

def getTxtSize(txt):
	lines = txt.replace('\r','').split("\n")
	w = 0
	for l in lines:
		w = max(w,len(l))
	return Size(w,len(lines))

def indentNotFirst(text,nb=1,spaces='  '):
	if text is not None:
		reg = re.compile(r'\n',re.M)  
		return re.sub(reg, "\n" + repeat(spaces, nb), text)
	else:
		return text
		
def indent(text,nb=1,spaces='  '):
	if text is not None:
		return spaces + indentNotFirst(text,nb,spaces)
	else:
		return text

def reverseStr(txt):
	return txt[::-1]
	
def removeCarret(txt, carretChar = '|'):
	tmp = '[[[[quoted_carret]]]]'
	return txt.replace(carretChar+carretChar, 'tmp') \
			.replace(carretChar, '') \
			.replace('tmp', carretChar)

def getAndRemoveFirstCarret(txt, carretChar = '|'):
	pos = getCarretPos(txt,carretChar)
	if pos is not None:
		txt = txt[0:pos] + txt[pos+len(carretChar):]
		return [pos,txt]
		
def getCarretPos(txt, carretChar = '|'):
	txt = txt.replace(carretChar+carretChar, ' ')
	if carretChar in txt :
		return txt.index(carretChar)
		
def isArray(arr):
	return isinstance(arr, list)

class PosCollection(object):
	def __init__(self, obj):
		self._wrapped_obj = obj

	def __getattr__(self, attr):
		if attr in self.__dict__:
			return getattr(self, attr)
		return getattr(self._wrapped_obj, attr)
		
	def __iter__(self):
			return self._wrapped_obj.__iter__()
			
	def wrap(self, prefix, suffix):
		return list(map( lambda p: Wrapping(p.start, p.end, prefix, suffix), self))
		
	def replace(self, txt):
		return list(map( lambda p: Replacement(p.start, p.end, txt), self))
		
def union(a1,a2):
	return list(set(a1).union(a2))

def merge(d1, *args):
	res = d1.copy()
	for d2 in args:
		res.update(d2)
	return res
