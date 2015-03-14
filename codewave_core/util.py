import re
	
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
class WrappedPos(Pos):
	def __init__(self,start,innerStart,innerEnd,end):
		self.start,self.innerStart,self.innerEnd,self.end = start,innerStart,innerEnd,end
	def innerContainsPt(self,pt):
		return self.innerStart <= pt and pt <= self.innerEnd
	def innerContainsPos(self,pos):
		return self.innerStart <= pos.start and pos.end <= self.innerEnd

class Size():
	def __init__(self,width,height):
		self.width,self.height = width,height

class Pair():
	def __init__(self, opener, closer, options):
		self.opener, self.closer, self.options = opener, closer, options
	def openerReg(self):
		if isinstance(self.opener, str) :
			return re.compile(util.escapeRegExp(self.opener))
		else:
			return self.opener
	def closerReg(self):
		if isinstance(self.closer, str) :
			return re.compile(util.escapeRegExp(self.closer))
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
			groups.append('('+reg.source+')')
		return re.compile('|'.join(groups))
	def matchAny(self,text):
		return re.match(self.matchAnyReg(),text)
	def matchAnyNamed(self,text):
		return self._matchAnyGetName(self.matchAny(text))
	def _matchAnyGetName(self,match):
		if match:
			for group, i in match.groups():
				if group is not None:
					return self.matchAnyPartKeys()[i-1]
			return None
	def matchAnyLast(self,text):
		ctext = text
		while True:
			match = self.matchAny(ctext)
			if match is None:
				break
			ctext = ctext.substr(match.index+1)
			res = match
		return res
	def matchAnyLastNamed(self,text):
		return self._matchAnyGetName(self.matchAnyLast(text))
	def isWapperOf(self,pos,text):
		return self.matchAnyNamed(text.substr(pos.end)) == 'closer' and self.matchAnyLastNamed(text.substr(0,pos.start)) == 'opener'
		

def splitFirstNamespace(fullname,isSpace = False) :
	if not ":" in fullname and not isSpace:
		return [None,fullname]
	parts = fullname.split(':')
	return [parts.pop(0), ':'.join(parts) or None]

def splitNamespace(fullname) :
	if ":" in fullname:
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
		

def union(a1,a2):
	return list(set(a1).union(a2))

def merge(d1, *args):
	res = d1.copy()
	for d2 in args:
		res.update(d2)
	return res
