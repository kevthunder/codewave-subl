

class Context():
	def __init__(self,codewave = None):
		self.codewave = codewave
		self.nameSpaces = []
		self._namespaces = self.commentChar = None
		self.parent = None
	def addNameSpace(self,name):
		if name not in self.nameSpaces :
			self.nameSpaces.append(name)
			self._namespaces = None
	def addNamespaces(self,spaces):
		if spaces :
			if isinstance(spaces, str):
				spaces = [spaces]
			for space in spaces :
				self.addNameSpace(space)
	def removeNameSpace(self,name):
		self.nameSpaces = [n for n in self.nameSpaces.filter if n != name]

	def getNameSpaces(self):
		if self._namespaces is None:
			npcs = set(['core']).union(self.nameSpaces)
			if self.parent is not None:
				npcs = npcs.union(self.parent.getNameSpaces())
			self._namespaces = list(npcs)
		return self._namespaces
	def getCmd(self,cmdName,nameSpaces = []):
		finder = self.getFinder(cmdName,nameSpaces)
		return finder.find()
	def getFinder(self,cmdName,nameSpaces = []):
		import codewave_core.cmd_finder as cmd_finder
		return cmd_finder.CmdFinder(cmdName, 
			namespaces= nameSpaces,
			useDetectors= self.isRoot(),
			codewave= self.codewave,
			parentContext= self
		)
	def isRoot(self):
		return not self.parent is not None
	def wrapComment(self,str):
		cc = self.getCommentChar()
		if '%s' in cc:
			return cc.replace('%s',str)
		else:
			return cc + ' ' + str + ' ' + cc
	def wrapCommentLeft(self,str = ''):
		cc = self.getCommentChar()
		i = cc.index('%s') if '%s' in cc else None
		if i is not None:
			return cc[0:i] + str
		else:
			return cc + ' ' + str
	def wrapCommentRight(self,str = ''):
		cc = self.getCommentChar()
		i = cc.index('%s') if '%s' in cc else None
		if i is not None:
			return str + cc[i+2:]
		else:
			return str + ' ' + cc
	def cmdInstanceFor(self,cmd):
		import codewave_core.cmd_instance as cmd_instance
		return cmd_instance.CmdInstance(cmd,self)
	def getCommentChar(self):
		if self.commentChar is not None:
			return self.commentChar
		cmd = self.getCmd('comment')
		char = '<!-- %s -->'
		if cmd is not None:
			inst = self.cmdInstanceFor(cmd)
			inst.content = '%s'
			res = inst.result()
			if res is not None:
				char = res
		self.commentChar = char
		return self.commentChar