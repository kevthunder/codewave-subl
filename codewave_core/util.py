import re
import codewave_core.logger as logger
	
class StrPos():
	def __init__(self,pos,str):
		self.pos,self.str = pos,str
	def end(self) :
		self.pos + len(self.str)

class Pos():
	def __init__(self,start,end):
		self.start,self.end = start,end
	def containsPt(self,pt):
		return self.start <= pt and pt <= self.end
	def containsPos(self,pos):
		return self.start <= pos.start and pos.end <= self.end
	def wrappedBy(self,prefix,suffix):
		return WrappedPos(self.start - len(prefix), self.start, self.end, self.end + len(suffix))
	def textFromEditor(self,editor):
		return editor.textSubstr(self.start, self.end)
	def applyOffset(self,offset):
		if offset != 0:
			self.start += offset
			self.end += offset
		return self
	def copy(self):
		return Pos(self.start,self.end)
		
class WrappedPos(Pos):
	def __init__(self,start,innerStart,innerEnd,end):
		self.start,self.innerStart,self.innerEnd,self.end = start,innerStart,innerEnd,end
	def innerContainsPt(self,pt):
		return self.innerStart <= pt and pt <= self.innerEnd
	def innerContainsPos(self,pos):
		return self.innerStart <= pos.start and pos.end <= self.innerEnd
	def innerTextFromEditor(self,editor):
		return editor.textSubstr(self.innerStart, self.innerEnd)
	def setInnerLen(self,len):
		self.moveSufix(self.innerStart + len)
	def moveSuffix(self,pt):
		suffixLen = self.end - self.innerEnd
		self.innerEnd = pt
		self.end = self.innerEnd + suffixLen
	def copy(self):
		return WrappedPos(self.start,self.innerStart,self.innerEnd,self.end)

class Size():
	def __init__(self,width,height):
		self.width,self.height = width,height

class Replacement(object):
	def __init__(self, start, end, text, prefix ='', suffix = ''):
		self.start, self.end, self.text, self.prefix, self.suffix = start, end, text, prefix, suffix
		self.selections = []
	def resPosBeforePrefix(self):
		return self.start+len(self.prefix)+len(self.text)
	def resEnd(self,editor = None): 
		return self.start+len(self.finalText(editor))
	def applyToEditor(self,editor):
		editor.spliceText(self.start, self.end, self.finalText(editor))
	def necessaryFor(self,editor):
		return self.finalText(editor) != editor.textSubstr(self.start, self.end)
	def originalTextWith(self,editor):
		return editor.textSubstr(self.start, self.end)
	def finalText(self,editor = None):
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
		res = Replacement(self.start, self.end, self.text, self.prefix, self.suffix)
		res.selections = list(map(lambda s: s.copy(), self.selections))
		return res
		
class Wrapping(Replacement):
	def __init__(self, start, end, prefix ='', suffix = ''):
		self.start, self.end, self.prefix, self.suffix = start, end, prefix, suffix
		self.text = ''
		self.selections = []
	def applyToEditor(self,editor):
		self.adjustSelFor(editor)
		super(self.__class__, self).applyToEditor(editor)
	def adjustSelFor(self,editor):
		offset = len(self.originalTextWith(editor))
		for sel in self.selections:
			if sel.start > self.start+len(self.prefix):
				sel.start += offset
			if sel.end >= self.start+len(self.prefix):
				sel.end += offset
	def finalText(self,editor = None):
		if editor is not None:
			text = self.originalTextWith(editor)
		else:
			text = ''
		return self.prefix+text+self.suffix
	def offsetAfter(self): 
		return len(self.prefix)+len(self.suffix)
					
	def copy(self): 
		res = Wrapping(self.start, self.end, self.prefix, self.suffix)
		res.selections = list(map(lambda s: s.copy(), self.selections))
		return res
		

class Pair():
	def __init__(self, opener, closer, options = {}):
		self.opener, self.closer, self.options = opener, closer, options
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
	def matchAny(self,text):
		return re.search(self.matchAnyReg(),text)
	def matchAnyNamed(self,text):
		return self._matchAnyGetName(self.matchAny(text))
	def _matchAnyGetName(self,match):
		if match:
			for i, group in enumerate(match.groups()):
				if group is not None:
					return self.matchAnyPartKeys()[i]
			return None
	def matchAnyLast(self,text):
		ctext = text
		while True:
			match = self.matchAny(ctext)
			if match is None:
				break
			ctext = ctext[match.start()+1:]
			res = match
		return res
	def matchAnyLastNamed(self,text):
		return self._matchAnyGetName(self.matchAnyLast(text))
	def isWapperOf(self,pos,text):
		return self.matchAnyNamed(text[pos.end:]) == 'closer' and self.matchAnyLastNamed(text[0:pos.start]) == 'opener'
		

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
	

def getTxtSize(txt):
	lines = txt.replace('\r','').split("\n")
	w = 0
	for l in lines:
		w = max(w,len(l))
	return Size(w,len(lines))
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
