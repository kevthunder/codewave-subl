import re
import codewave_core.codewave
import codewave_core.cmd_instance as cmd_instance
import codewave_core.util as util
import codewave_core.logger as logger
import codewave_core.command as command
import codewave_core.text_parser as text_parser
import codewave_core.box_helper as box_helper

class PositionedCmdInstance(cmd_instance.CmdInstance):
	def __init__(self, codewave,pos,str):
		super(self.__class__, self).__init__()
		self.codewave,self.pos,self.str = codewave,pos,str
		self.replaceStart = self.replaceEnd = None
		self.multiPos = self.inBox = self.closingPos = None
		self._prevEOL = self._nextEOL = self._rawWithFullLines = self._sameLinesPrefix = self._sameLinesSuffix = None
		self.inited = False
		if not self.isEmpty():
			self._checkCloser()
			self.opening = self.str
			self.noBracket = self._removeBracket(self.str)
			self._splitComponents()
			self._findClosing()
			self._checkElongated()
	def _checkCloser(self):
		noBracket = self._removeBracket(self.str)
		if noBracket[0:len(self.codewave.closeChar)] == self.codewave.closeChar :
			f = self._findOpeningPos()
			if f is not None :
				self.closingPos = util.StrPos(self.pos, self.str)
				self.pos = f.pos
				self.str = f.str
	def _findOpeningPos(self):
		cmdName = self._removeBracket(self.str)[len(self.codewave.closeChar):]
		opening = self.codewave.brakets + cmdName
		closing = self.str
		f = self.codewave.findMatchingPair(self.pos,opening,closing,-1)
		if f is not None :
			f.str = self.codewave.editor.textSubstr(f.pos,self.codewave.findNextBraket(f.pos+len(f.str))+len(self.codewave.brakets))
			return f
	def _splitComponents(self):
		parts = self.noBracket.split(" ");
		self.cmdName = parts.pop(0)
		self.rawParams = " ".join(parts)
	def _parseParams(self,params):
		self.params = []
		self.named = {}
		if self.cmd is not None: 
			self.named.update(self.cmd.getDefaults())
			nameToParam = self.getOption('nameToParam')
			if nameToParam is not None :
				self.named[nameToParam] = self.cmdName
		if len(params):
			if self.cmd is not None:
				allowedNamed = self.getOption('allowedNamed')
			inStr = False
			param = ''
			name = False
			for i in range(0,len(params)):
				chr = params[i]
				if chr == ' ' and not inStr:
					if(name):
						self.named[name] = param
					else:
						self.params.append(param)
					param = ''
					name = False
				elif chr == '"' and (i == 0 or params[i-1] != '\\'):
					inStr = not inStr
				elif chr == ':' and not name and not inStr and (allowedNamed is None or name in allowedNamed):
					name = param
					param = ''
				else:
					param += chr
			if len(param):
				if(name):
					self.named[name] = param
				else:
					self.params.append(param)
	def _findClosing(self):
		f = self._findClosingPos()
		if f is not None:
			self.content = util.trimEmptyLine(self.codewave.editor.textSubstr(self.pos+len(self.str),f.pos))
			self.str = self.codewave.editor.textSubstr(self.pos,f.pos+len(f.str))
	def _findClosingPos(self):
		if self.closingPos is not None :
			return self.closingPos
		closing = self.codewave.brakets + self.codewave.closeChar + self.cmdName + self.codewave.brakets
		opening = self.codewave.brakets + self.cmdName
		f = self.codewave.findMatchingPair(self.pos+len(self.str), opening, closing)
		if f is not None:
			self.closingPos = f
			return self.closingPos
	def _checkElongated(self):
		endPos = self.getEndPos()
		max = self.codewave.editor.textLen()
		while endPos < max and self.codewave.editor.textSubstr(endPos,endPos+len(self.codewave.deco)) == self.codewave.deco:
			endPos+=len(self.codewave.deco)
		if endPos >= max or self.codewave.editor.textSubstr(endPos, endPos + len(self.codewave.deco)) in [' ',"\n","\r"]:
			self.str = self.codewave.editor.textSubstr(self.pos,endPos)
	def _checkBox(self):
		if self.codewave.inInstance is not None and self.codewave.inInstance.cmd.name == 'comment':
			return
		cl = self.context.wrapCommentLeft()
		cr = self.context.wrapCommentRight()
		endPos = self.getEndPos() + len(cr)
		if self.codewave.editor.textSubstr(self.pos - len(cl),self.pos) == cl and self.codewave.editor.textSubstr(endPos - len(cr),endPos) == cr:
			self.pos = self.pos - len(cl)
			self.str = self.codewave.editor.textSubstr(self.pos,endPos)
			self._removeCommentFromContent()
		elif cl in self.sameLinesPrefix() and cr in self.sameLinesSuffix():
			self.inBox = 1
			self._removeCommentFromContent()
	def _removeCommentFromContent(self):
		if self.content:
			ecl = util.escapeRegExp(self.context.wrapCommentLeft())
			ecr = util.escapeRegExp(self.context.wrapCommentRight())
			ed = util.escapeRegExp(self.codewave.deco)
			re1 = re.compile("^\\s*"+ecl+"(?:"+ed+")+\\s*(.*?)\\s*(?:"+ed+")+"+ecr+"$", re.M)
			re2 = re.compile("^\\s*(?:"+ed+")*"+ecr+"\r?\n")
			re3 = re.compile("\n\\s*"+ecl+"(?:"+ed+")*\\s*$")
			self.content = re.sub(re3,'',re.sub(re2,'',re.sub(re1,r'\1',self.content)))
	def _getParentCmds(self):
		p = self.codewave.getEnclosingCmd(self.getEndPos())
		self.parent = p.init() if p is not None else None
	def setMultiPos(self,multiPos):
		self.multiPos = multiPos
	def prevEOL(self):
		if self._prevEOL is None:
			self._prevEOL = self.codewave.findLineStart(self.pos)
		return self._prevEOL
	def nextEOL(self):
		if self._nextEOL is None:
			self._nextEOL = self.codewave.findLineEnd(self.getEndPos())
		return self._nextEOL
	def rawWithFullLines(self):
		if self._rawWithFullLines is None:
			self._rawWithFullLines = self.codewave.editor.textSubstr(self.prevEOL(),self.nextEOL())
		return self._rawWithFullLines
	def sameLinesPrefix(self):
		if self._sameLinesPrefix is None:
			self._sameLinesPrefix = self.codewave.editor.textSubstr(self.prevEOL(),self.pos)
		return self._sameLinesPrefix
	def sameLinesSuffix(self):
		if self._sameLinesSuffix is None:
			self._sameLinesSuffix = self.codewave.editor.textSubstr(self.getEndPos(),self.nextEOL())
		return self._sameLinesSuffix
	def _getCmdObj(self):
		self.getCmd()
		self._checkBox()
		self.content = self.removeIndentFromContent(self.content)
		super(PositionedCmdInstance, self)._getCmdObj()
	def _initParams(self):
		self._parseParams(self.rawParams)
	def getContext(self):
		return self.context or self.codewave.context
	def getCmd(self):
		if self.cmd is None:
			self._getParentCmds()
			if self.noBracket[0:len(self.codewave.noExecuteChar)] == self.codewave.noExecuteChar:
				self.cmd = command.cmds.getCmd('core:no_execute')
				self.context = self.codewave.context
			else:
				self.finder = self.getFinder(self.cmdName)
				self.context = self.finder.context
				self.cmd = self.finder.find()
				if self.cmd is not None:
					self.context.addNameSpace(self.cmd.fullName)
		return self.cmd
	def getFinder(self,cmdName):
		finder = self.codewave.context.getFinder(cmdName,self._getParentNamespaces())
		finder.instance = self
		return finder
	def _getParentNamespaces(self):
		nspcs = []
		obj = self
		while obj.parent is not None:
			obj = obj.parent
			if obj.cmd is not None and obj.cmd.fullName is not None:
				nspcs.append(obj.cmd.fullName) 
		return nspcs
	def _removeBracket(self,str):
		return str[len(self.codewave.brakets):len(str)-len(self.codewave.brakets)]
	def isEmpty(self):
		return self.str == self.codewave.brakets + self.codewave.closeChar + self.codewave.brakets or self.str == self.codewave.brakets + self.codewave.brakets
	def execute(self):
		if self.isEmpty():
			if self.codewave.closingPromp is not None and self.codewave.closingPromp.whithinOpenBounds(self.pos + len(self.codewave.brakets)) is not None:
				self.codewave.closingPromp.cancel()
			else:
				self.replaceWith('')
		elif self.cmd is not None:
			beforeFunct = self.getOption('beforeExecute')
			if beforeFunct is not None:
				beforeFunct(self)
			if self.resultIsAvailable():
				res = self.result()
				if res is not None:
					self.replaceWith(res)
					return True
			else:
				return self.runExecuteFunct()
	def getEndPos(self):
		return self.pos+len(self.str)
	def getPos(self):
		return util.Pos(self.pos,self.pos+len(self.str))
	def getIndent(self):
		if self.indentLen is None:
			if self.inBox is not None:
				helper = box_helper.BoxHelper(self.context)
				self.indentLen = len(helper.removeComment(self.sameLinesPrefix()))
			else:
				self.indentLen = self.pos - self.codewave.findLineStart(self.pos)
		return self.indentLen
	def removeIndentFromContent(self,text):
		if text is not None:
			reg = re.compile('^\\s{'+str(self.getIndent())+'}',re.M)
			return re.sub(reg,'',text)
		else:
			return text
	def alterResultForBox(self,repl):
		helper = box_helper.BoxHelper(self.context)
		helper.getOptFromLine(self.rawWithFullLines(),False)
		if self.getOption('replaceBox'):
			box = helper.getBoxForPos(self.getPos())
			repl.start, repl.end = box.start, box.end
			self.indentLen = helper.indent
			repl.text = self.applyIndent(repl.text)
		else:
			repl.text = self.applyIndent(repl.text)
			repl.start = self.prevEOL()
			repl.end = self.nextEOL()
			res = helper.reformatLines(self.sameLinesPrefix() + self.codewave.marker + repl.text + self.codewave.marker + self.sameLinesSuffix(), {'multiline':False})
			repl.prefix,repl.text,repl.suffix = res.split(self.codewave.marker)
		return repl
	def getCursorFromResult(self,repl):
		cursorPos = repl.resPosBeforePrefix()
		if self.cmd is not None and self.codewave.checkCarret and self.getOption('checkCarret'):
			p = self.codewave.getCarretPos(repl.text)
			if p is not None :
				cursorPos = repl.start+len(repl.prefix)+p
			repl.text = self.codewave.removeCarret(repl.text)
		return cursorPos
	def checkMulti(self,repl):
		if self.multiPos is not None and len(self.multiPos) > 1:
			replacements = [repl]
			originalText = repl.originalTextWith(self.codewave.editor)
			for i, pos in enumerate(self.multiPos):
				if i == 0:
					originalPos = pos.start
				else:
					newRepl = repl.copy().applyOffset(pos.start-originalPos)
					if newRepl.originalTextWith(self.codewave.editor) == originalText:
						replacements.append(newRepl)
					logger.log(replacements)
			return replacements
		else:
			return [repl]
	def replaceWith(self,text):
		repl =  util.Replacement(self.pos,self.getEndPos(),text)
		
		if self.inBox is not None:
			self.alterResultForBox(repl)
		else:
			repl.text = self.applyIndent(repl.text)
			
		cursorPos = self.getCursorFromResult(repl)
		repl.selections = [util.Pos(cursorPos, cursorPos)]
		replacements = self.checkMulti(repl)
		self.codewave.editor.applyReplacements(replacements)

		self.replaceStart = repl.start
		self.replaceEnd = repl.resEnd()