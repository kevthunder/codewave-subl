import re
import codewave_core.util as util
import codewave_core.logger as logger

class BoxHelper():
	def __init__(self, context, options = {}):
		self.context = context
		self.defaults = {
			'deco': self.context.codewave.deco,
			'pad': 2,
			'width': 50,
			'height': 3,
			'openText': '',
			'closeText': '',
			'prefix': '',
			'suffix': '',
			'indent': 0
		}
		for key, val in self.defaults.items():
			if key in options:
				setattr(self,key,options[key])
			else:
				setattr(self,key,val)
	def clone(self):
		opt = {}
		for key, val in self.defaults.items():
				opt[key] = getattr(self,key)
		return BoxHelper(self.context,opt)
	def draw(self,text):
		return self.startSep() + "\n" + self.lines(text) + "\n"+ self.endSep()
	def wrapComment(self,str):
		return self.context.wrapComment(str)
	def separator(self):
		len = self.width + 2 * self.pad + 2 * len(self.deco)
		return self.wrapComment(self.decoLine(len))
	def startSep(self):
		ln = self.width + 2 * self.pad + 2 * len(self.deco) - len(self.openText)
		return self.prefix + self.wrapComment(self.openText+self.decoLine(ln))
	def endSep(self):
		ln = self.width + 2 * self.pad + 2 * len(self.deco) - len(self.closeText)
		return self.wrapComment(self.closeText+self.decoLine(ln)) + self.suffix
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
	def left(self):
		return self.context.wrapCommentLeft(self.deco + self.padding())
	def right(self):
		return self.context.wrapCommentRight(self.padding() + self.deco)
	def removeIgnoredContent(self,text):
		return self.context.codewave.removeMarkers(self.context.codewave.removeCarret(text))
	def textBounds(self,text):
		return util.getTxtSize(self.removeIgnoredContent(text))
	def getBoxForPos(self,pos):
		depth = self.getNestedLvl(pos.start)
		if depth > 0:
			left = self.left()
			curLeft = util.repeat(left,depth-1)
			
			clone = self.clone()
			placeholder = "###PlaceHolder###"
			clone.width = len(placeholder)
			clone.openText = clone.closeText = self.deco + self.deco + placeholder + self.deco + self.deco
			escPlaceholder = util.escapeRegExp("###PlaceHolder###")
			
			
			startFind = re.compile(util.escapeRegExp(curLeft + clone.startSep()).replace(escPlaceholder,'.*'))
			endFind = re.compile(util.escapeRegExp(curLeft + clone.endSep()).replace(escPlaceholder,'.*'))
			
			
			pair = util.Pair(startFind,endFind,{
				'validMatch': self.validPairMatch
			})
			res = pair.wrapperPos(pos,self.context.codewave.editor.text)
			
			if res is not None:
				res.start += len(curLeft)
				return res

	def validPairMatch(self,match):
		left = self.left()
		f = self.context.codewave.findAnyNext(match.start() ,[left,"\n","\r"],-1)
		return not f is not None or f.str != left

	def getNestedLvl(self,index):
		depth = 0
		left = self.left()
		while True:
			f = self.context.codewave.findAnyNext(index ,[left,"\n","\r"],-1)
			if f is None or f.str != left:
					break
			index = f.pos
			depth+=1
		return depth
	def getOptFromLine(self,line,getPad=True):
		rStart = re.compile("(\\s*)("+util.escapeRegExp(self.context.wrapCommentLeft(self.deco))+")(\\s*)")
		rEnd = re.compile("(\\s*)("+util.escapeRegExp(self.context.wrapCommentRight(self.deco))+")(\n|$)")
		resStart = rStart.search(line)
		resEnd = rEnd.search(line)
		if resStart is not None and resEnd is not None:
			if getPad:
				self.pad = min(len(resStart.group(3)),len(resEnd.group(1)))
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
			ecl = util.escapeRegExp(self.context.wrapCommentLeft())
			ecr = util.escapeRegExp(self.context.wrapCommentRight())
			ed = util.escapeRegExp(self.deco)
			flag = re.M if opt['multiline'] else 0
			re1 = re.compile("^\\s*"+ecl+"(?:"+ed+")*\\s{0,"+str(self.pad)+"}", flag)
			re2 = re.compile("\\s*(?:"+ed+")*"+ecr+"\\s*$", flag)
			return re.sub(re2,'',re.sub(re1,'',text))