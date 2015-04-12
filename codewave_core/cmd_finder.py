import codewave_core.command as command
import codewave_core.core_cmds as core_cmds
import codewave_core.logger as logger
import codewave_core.util as util
import codewave_core.context as context

class CmdFinder():
	def __init__(self,names, **options):
		
		if isinstance(names, str):
			names = [names]
		defaults = {
			'parent' : None,
			'namespaces' : [],
			'parentContext': None,
			'context': None,
			'root' : command.cmds,
			'mustExecute': True,
			'useDetectors': True,
			'useFallbacks': True,
			'instance': None,
			'codewave': None
		}
		self.names = names
		self.parent = options['parent'] if 'parent' in options else None
		for key, val in defaults.items():
			if key in options:
				setattr(self,key,options[key])
			elif self.parent is not None and key != 'parent':
				setattr(self,key,getattr(self.parent,key))
			else:
				setattr(self,key,val)
		if self.context is None:
			self.context = context.Context(self.codewave)
		if self.parentContext is not None:
			self.context.parent = self.parentContext
		if self.namespaces is not None:
			self.context.addNamespaces(self.namespaces)
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
		if rest is not None:
			name = rest + ':' + name
		return name
	def getDirectNames(self):
		return [n for n in self.names if ':' not in n]
	def triggerDetectors(self):
		if self.useDetectors :
			self.useDetectors = False
			posibilities = CmdFinder(self.context.getNameSpaces(), parent=self, mustExecute=False, useFallbacks=False).findPosibilities()
			i = 0
			while i < len(posibilities):
				cmd = posibilities[i]
				for detector in cmd.detectors :
					res = detector.detect(self)
					if res is not None:
						self.context.addNamespaces(res)
						posibilities += CmdFinder(res, parent = self, mustExecute = False, useFallbacks = False).findPosibilities()
				i+=1
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
			next = self.getCmdFollowAlias(space)
			if next is not None :
				posibilities += CmdFinder(names, parent=self, root=next).findPosibilities()
		for nspc in self.context.getNameSpaces():
			nspcName,rest = util.splitFirstNamespace(nspc,True)
			next = self.getCmdFollowAlias(nspcName)
			if next is not None :
				posibilities += CmdFinder(self.applySpaceOnNames(nspc), parent=self, root=next).findPosibilities()
		for name in self.getDirectNames():
			direct = self.root.getCmd(name)
			if self.cmdIsValid(direct):
				posibilities.append(direct)
		if self.useFallbacks:
			fallback = self.root.getCmd('fallback')
			if self.cmdIsValid(fallback):
				posibilities.append(fallback)
		return posibilities
	def getCmdFollowAlias(self,name):
		cmd = self.root.getCmd(name)
		if cmd is not None :
			cmd.init()
			if cmd.aliasOf is not None:
				return cmd.getAliased()
		return cmd
	def cmdIsValid(self,cmd):
		if cmd is None:
			return False
		cmd.init()
		return not self.mustExecute or cmd.isExecutable()
	def cmdScore(self,cmd):
		score = cmd.depth
		if cmd.name == 'fallback' :
			score -= 1000
		return score
	def bestInPosibilities(self,poss):
		if len(poss) > 0:
			best = None
			bestScore = None
			for p in poss:
				score = self.cmdScore(p)
				if best is None or score >= bestScore:
					bestScore = score
					best = p
			return best;