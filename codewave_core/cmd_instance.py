import re
import codewave_core.codewave
import codewave_core.util as util
import codewave_core.logger as logger
import codewave_core.command as command
import codewave_core.text_parser as text_parser
import codewave_core.box_helper as box_helper

class CmdInstance(object):
	def __init__(self, cmd = None, context = None):
		self.cmd,self.context = cmd,context
		self.content = self.cmdObj = None
		self.indentLen = self.cmd = self.aliasedCmd = self.aliasedFinalCmd = self.cmdOptions = None
		
	def init(self):
		if not self.isEmpty() or self.inited:
			self.inited = True
			self._getCmdObj()
			self._initParams()
			if self.cmdObj is not None:
				self.cmdObj.init()
		return self
	def setParam(self,name,val):
		self.named[name] = val
	def pushParam(self,val):
		self.params.append(val)
	def getContext(self):
		if self.context is None:
			self.context = context.Context()
		return self.context or context.Context()
	def getFinder(self,cmdName):
		finder = self.getContext().getFinder(cmdName,self._getParentNamespaces())
		finder.instance = self
		return finder
	def _getCmdObj(self):
		if self.cmd is not None:
			self.cmd.init()
			cmd = self.getAliased() or self.cmd
			cmd.init()
			if cmd.cls is not None:
				self.cmdObj = cmd.cls(self)
				return self.cmdObj
	def _initParams(self):
		self.named = self.getDefaults()
	def _getParentNamespaces(self):
		return array()
	def isEmpty(self):
		return self.cmd is not None
	def resultIsAvailable(self):
		if self.cmd is not None:
			if self.cmdObj is not None:
				return self.cmdObj.resultIsAvailable()
			aliased = self.getAliasedFinal()
			if aliased is not None:
				return aliased.resultIsAvailable()
			return self.cmd.resultIsAvailable()
		return False
	def getDefaults(self):
		if self.cmd is not None:
			res = {}
			aliased = self.getAliased()
			if aliased is not None:
				res = util.merge(res,aliased.getDefaults())
			res = util.merge(res,cmd.defaults)
			if self.cmdObj is not None:
				res = util.merge(res,self.cmdObj.getDefaults())
			return res
	def getAliased(self):
		if self.cmd is not None:
			if self.aliasedCmd is None:
				self.getAliasedFinal()
			return self.aliasedCmd or None
	def getAliasedFinal(self):
		if self.cmd is not None:
			if self.aliasedFinalCmd is not None:
				return self.aliasedFinalCmd or None
			if self.cmd.aliasOf is not None:
				aliased = self.cmd
				while aliased is not None and aliased.aliasOf is not None:
					nspc, cmdName = util.splitNamespace(self.cmdName)
					aliasOf = aliased.aliasOf.replace('%name%',cmdName)
					aliased = aliased._aliasedFromFinder(self.getFinder(aliasOf))
					if self.aliasedCmd is None:
						self.aliasedCmd = aliased or False
				self.aliasedFinalCmd = aliased or False
				return aliased
	def getOptions(self):
		if self.cmd is not None:
			if self.cmdOptions is not None:
				return self.cmdOptions
			opt = self.cmd._optionsForAliased(self.getAliased())
			if self.cmdObj is not None:
				opt = util.merge(opt,self.cmdObj.getOptions())
			self.cmdOptions = opt
			return opt
	def getOption(self,key):
		options = self.getOptions()
		if options is not None and key in options:
			return options[key]
	def getParam(self,names, defVal = None):
		if type(names) is not list :
			names = [names]
		for n in names:
			if isinstance( n, int ) and n < len(self.params) :
				return self.params[n] 
			if n in self.named :
				return self.named[n] 
		return defVal
	def runExecuteFunct(self):
		if self.cmd is not None:
			if self.cmdObj is not None:
				return self.cmdObj.execute()
			cmd = self.getAliasedFinal() or self.cmd
			cmd.init()
			if cmd.executeFunct is not None:
				return cmd.executeFunct(self)
	def rawResult(self):
		if self.cmd is not None:
			if self.cmdObj is not None:
				return self.cmdObj.result()
			cmd = self.getAliasedFinal() or self.cmd
			cmd.init()
			if cmd.resultFunct is not None:
				return cmd.resultFunct(self)
			if cmd.resultStr is not None:
				return cmd.resultStr
	def result(self): 
		self.init()
		if self.resultIsAvailable():
			res = self.rawResult()
			if res is not None:
				res = self.formatIndent(res)
				if len(res) > 0 and self.getOption('parse') :
					parser = self.getParserForText(res)
					res = parser.parseAll()
				alterFunct = self.getOption('alterResult')
				if alterFunct is not None:
					res = alterFunct(res,self)
				return res
	def getParserForText(self,txt=''):
		parser = codewave_core.codewave.Codewave(text_parser.TextParser(txt), inInstance=self)
		parser.checkCarret = False
		return parser
	def getIndent(self):
		return 0
	def formatIndent(self,text):
		if text is not None:
			return text.replace("\t",'  ')
		else:
			return text
	def applyIndent(self,text):
		if text is not None:
			reg = re.compile(r'\n',re.M)
			return re.sub(reg, "\n" + util.repeatToLength(" ",self.getIndent()),text)
		else:
			return text