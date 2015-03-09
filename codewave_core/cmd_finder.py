import codewave_core.command as command
import codewave_core.core_cmds as core_cmds
import codewave_core.logger as logger
import codewave_core.util as util

class CmdFinder():
	def __init__(self,names,namespaces = None, parent=None, **keywords):
		if not isinstance(names, list) :
			names = [names]
		defaults = {
			'namespaces' : [],
			'root' : command.cmds,
			'mustExecute': True,
			'useDetectors': True,
			'useFallbacks': True,
			'instance': None,
			'codewave': None
		}
		self.names = names
		self.parent = parent
		if namespaces is not None :
			keywords['namespaces'] = namespaces 
		for key, val in defaults.items():
			if key in keywords:
				setattr(self,key,keywords[key])
			elif parent is not None :
				setattr(self,key,getattr(parent,key))
			else:
				setattr(self,key,val)
	def find(self):
		self.triggerDetectors()
		self.cmd = self.findIn(self.root)
		return self.cmd
	def getPosibilities(self):
		self.triggerDetectors()
		path = list(self.path)
		return self.findPosibilitiesIn(self.root,path)
	def getNamesWithPaths(self):
		paths = {}
		for name in self.names :
			space,rest = util.splitFirstNamespace(name)
			if space is not None and space not in self.namespaces:
				if space not in paths :
					paths[space] = []
				paths[space].append(rest)
		return paths
	def applySpaceOnNames(self,namespace):
		space,rest = util.splitFirstNamespace(namespace,True)
		return list(map(lambda n: self._applySpaceOnName(n,space,rest) , self.names))
	def _applySpaceOnName(self,name,space,rest):
		cur_space,cur_rest = util.splitFirstNamespace(name)
		if cur_space is not None and cur_space == space:
			name = cur_rest
		if rest is not None :
			name = rest + ':' + name
		return name
	def getDirectNames(self):
		return [n for n in self.names if ':' not in n]
	def triggerDetectors(self):
		if self.useDetectors :
			self.useDetectors = False
			posibilities = CmdFinder(self.namespaces,parent=self,mustExecute=False,useFallbacks=False).findPosibilities()
			i = 0
			while i < len(posibilities):
				cmd = posibilities[i]
				for detector in cmd.detectors :
					res = detector.detect(self)
					if res is not None:
						self.addNamespaces(res)
						posibilities += CmdFinder(res, parent = self, mustExecute = False, useFallbacks = False).findPosibilities()
				i+=1
	def addNamespaces(self,spaces):
		if spaces :
			if not isinstance(spaces, list) :
				spaces = [spaces]
			for space in spaces :
				if space not in self.namespaces :
					self.namespaces.append(space)
	def findIn(self,cmd,path = None):
		if cmd is None:
			return None
		best = self.bestInPosibilities(self.findPosibilities())
		if best is not None:
			return best
	def findPosibilities(self):
		if self.root is None:
			return []
		self.root.init()
		posibilities = []
		for space, names in self.getNamesWithPaths().items():
			next = self.root.getCmd(space)
			if next is not None :
				posibilities += CmdFinder(names,parent=self,root=next).findPosibilities()
		for nspc in self.namespaces:
			nspcName,rest = util.splitFirstNamespace(nspc,True)
			next = self.root.getCmd(nspcName)
			if next is not None :
				posibilities += CmdFinder(self.applySpaceOnNames(nspc),parent=self,root=next).findPosibilities()
		for name in self.getDirectNames():
			direct = self.root.getCmd(name)
			if self.cmdIsValid(direct):
				posibilities.append(direct)
		if self.useFallbacks:
			fallback = self.root.getCmd('fallback')
			if self.cmdIsValid(fallback):
				posibilities.append(fallback)
		return posibilities
	def cmdIsValid(self,cmd):
		if cmd is None:
			return False
		cmd.init()
		return not self.mustExecute or cmd.isExecutable()
	def bestInPosibilities(self,poss):
		if len(poss) > 0:
			best = None
			bestScore = None
			for p in poss:
				score = p.depth
				if p.name == 'fallback' :
						score -= 1000
				if best is None or score >= bestScore:
					bestScore = score
					best = p
			return best;