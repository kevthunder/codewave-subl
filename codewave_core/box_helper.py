import re
import codewave_core.util as util
import codewave_core.logger as logger

class BoxHelper():
	def __init__(self, codewave, options = {}):
		self.codewave = codewave
		defaults = {
			'deco': codewave.deco,
			'pad': 2,
			'width': 50,
			'height': 3,
			'openText': '',
			'closeText': '',
			'indent': 0
		}
		for key, val in defaults.items():
			if key in options:
				setattr(self,key,options[key])
			else:
				setattr(self,key,val)
	def draw(self,text):
		return self.startSep() + "\n" + self.lines(text) + "\n"+ self.endSep()
	def wrapComment(self,str):
		return self.codewave.wrapComment(str)
	def separator(self):
		len = self.width + 2 * self.pad + 2 * len(self.deco)
		return self.wrapComment(self.decoLine(len))
	def startSep(self):
		ln = self.width + 2 * self.pad + 2 * len(self.deco) - len(self.openText)
		return self.wrapComment(self.openText+self.decoLine(ln))
	def endSep(self):
		ln = self.width + 2 * self.pad + 2 * len(self.deco) - len(self.closeText)
		return self.wrapComment(self.closeText+self.decoLine(ln))
	def decoLine(self,len):
		return util.repeatToLength(self.deco, len)
	def padding(self): 
		return util.repeatToLength(" ", self.pad)
	def lines(self,text = '', uptoHeight=True):
		text = text or ''
		lines = text.replace('\r', '').split("\n")
		if uptoHeight:
			return "\n".join([self.line(lines[x] if x < len(lines) else '') for x in range(0,self.height)]) 
		else:
			return "\n".join([self.line(l) for l in lines]) 
	def line(self,text = ''):
		return (util.repeatToLength(" ",self.indent) +
			self.wrapComment(
					self.deco + 
					self.padding() + 
					text + 
					util.repeatToLength(" ", self.width - len(self.removeIgnoredContent(text))) + 
					self.padding() + 
					self.deco
			))
	def removeIgnoredContent(self,text):
		return self.codewave.removeMarkers(self.codewave.removeCarret(text))
	def textBounds(self,text):
		return util.getTxtSize(self.removeIgnoredContent(text))
	def getBoxForPos(self,pos):
		startFind = self.codewave.wrapCommentLeft(self.deco + self.deco)
		endFind = self.codewave.wrapCommentRight(self.deco + self.deco)
		start = self.codewave.findPrev(pos.start, startFind)
		end = self.codewave.findNext(pos.end, endFind)
		if start is not None and end is not None:
			 return util.Pos(start,end + len(endFind))
	def getOptFromLine(self,line,getPad=True):
		rStart = re.compile("(\\s*)("+self.codewave.wrapCommentLeft(self.deco)+")(\\s*)")
		rEnd = re.compile("(\\s*)("+self.codewave.wrapCommentRight(self.deco)+")")
		resStart = rStart.search(line)
		resEnd = rEnd.search(line)
		if getPad:
			self.pad = Math.min(len(resStart.group(3)),len(resEnd.group(1)))
		self.indent = len(resStart.group(1))
		startPos = resStart.end(2) + self.pad
		endPos = resEnd.start(2) - self.pad
		self.width = endPos - startPos
		return self
	def reformatLines(self,text,options={}):
		return self.lines(self.removeComment(text,options),False)
	def removeComment(self,text,options={}):
		if text is not None:
			defaults = {
				'multiline': True
			}
			opt = util.merge(defaults,options)
			ecl = util.escapeRegExp(self.codewave.wrapCommentLeft())
			ecr = util.escapeRegExp(self.codewave.wrapCommentRight())
			ed = util.escapeRegExp(self.deco)
			flag = re.M if opt['multiline'] else 0
			re1 = re.compile("^\\s*"+ecl+"(?:"+ed+")*\\s{0,"+str(self.pad)+"}",flag)
			re2 = re.compile("\\s*(?:"+ed+")*"+ecr+"\\s*$",flag)
			return re.sub(re2,'',re.sub(re1,'',text))