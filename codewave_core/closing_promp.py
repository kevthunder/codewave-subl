import codewave_core.logger as logger
import codewave_core.util as util

class ClosingPromp():
	def __init__(self, codewave,selections):
		self.codewave = codewave
		self._typed = None
		self.selections = util.PosCollection(selections)
	def begin(self):
		self.started = True
		self.addCarrets()
		if self.codewave.editor.canListenToChange():
			self.codewave.editor.addChangeListener( self.onChange )
		return self
	def addCarrets(self):
		self.replacements = list(map(lambda p: p.carretToSel(), self.selections.wrap(
			self.codewave.brakets + self.codewave.carretChar + self.codewave.brakets + "\n",
			"\n" + self.codewave.brakets + self.codewave.closeChar + self.codewave.carretChar + self.codewave.brakets
		)))
		self.codewave.editor.applyReplacements(self.replacements)
	def invalidTyped(self):
		self._typed = None
	def onChange(self,ch = None):
		self.invalidTyped()
		if self.skipEvent(ch):
			return
		if self.shouldStop():
			self.stop()
			self.cleanClose()
		else:
			self.resume()
			
	def skipEvent(self,ch):
		return ch is not None and ch.charCodeAt(0) != 32
	
	def resume(self):
		pass
		
	def shouldStop(self):
		return self.typed() == False or ' ' in self.typed()
	
	def cleanClose(self):
		replacements = []
		selections = self.getSelections()
		for sel in selections:
			pos = self.whithinOpenBounds(sel)
			if pos is not None:
				start = sel
			else:
				end = self.whithinCloseBounds(sel)
				if end is not None and start is not None:
					res = end.innerTextFromEditor(self.codewave.editor).split(' ')[0]
					repl = util.Replacement(end.innerStart,end.innerEnd,res)
					repl.selections = [start]
					replacements.append(repl)
					start = None
		self.codewave.editor.applyReplacements(replacements)
	def getSelections(self):
		self.codewave.editor.getMultiSel()
	def stop(self):
		self.started = False
		if self.codewave.closingPromp == self:
			self.codewave.closingPromp = None 
		if self.proxyOnChange is not None:
			self.codewave.editor.removeChangeListener(self.proxyOnChange)
	def cancel(self):
		if self.typed() != False:
			self.cancelSelections(self.getSelections())
		self.stop()
	def cancelSelections(self,selections):
		replacements = []
		start = None
		for sel in selections:
			pos = self.whithinOpenBounds(sel)
			if pos is not None:
				start = pos
			else:
				end = self.whithinCloseBounds(sel)
				if end is not None and start is not None:
					start = None
					replacements.append(util.Replacement(start.start,end.end,self.codewave.editor.textSubstr(start.end+1, end.start-1)).selectContent())
		self.codewave.editor.applyReplacements(self.replacements)
	def typed(self):
		if self._typed is None:
			cpos = self.codewave.editor.getCursorPos()
			innerStart = self.replacements[0].start + len(self.codewave.brakets)
			if self.codewave.findPrevBraket(cpos.start) == self.replacements[0].start :
				innerEnd = self.codewave.findNextBraket(innerStart)
				if innerEnd is not None and innerEnd >= cpos.end:
					self._typed = self.codewave.editor.textSubstr(innerStart, innerEnd)
				else:
					self._typed = False
			else:
				self._typed = False
		return self._typed
	def whithinOpenBounds(self,pos):
		for i, repl in enumerate(self.replacements):
			targetPos = self.startPosAt(i)
			targetText = self.codewave.brakets + self.typed() + self.codewave.brakets
			if targetPos.innerContainsPos(pos) and targetPos.textFromEditor(self.codewave.editor) == targetText:
				return targetPos
		return False
	def whithinCloseBounds(self,pos):
		for i, repl in enumerate(self.replacements):
			targetPos = self.endPosAt(i)
			targetText = self.codewave.brakets + self.codewave.closeChar + self.typed() + self.codewave.brakets
			if targetPos.innerContainsPos(pos) and targetPos.textFromEditor(self.codewave.editor) == targetText:
				return targetPos
		return False
	def startPosAt(self,index):
		return util.Pos(
				self.replacements[index].selections[0].start + len(self.typed()) * (index*2),
				self.replacements[index].selections[0].end + len(self.typed()) * (index*2 +1)
			).wrappedBy(self.codewave.brakets, self.codewave.brakets)
	def endPosAt(self,index):
		return util.Pos(
				self.replacements[index].selections[1].start + len(self.typed()) * (index*2 +1),
				self.replacements[index].selections[1].end + len(self.typed()) * (index*2 +2)
			).wrappedBy(self.codewave.brakets + self.codewave.closeChar, self.codewave.brakets)

class SimulatedClosingPromp(ClosingPromp):
	def resume(self):
		self.simulateType()
	def simulateType(self):
		targetText = self.codewave.brakets + self.codewave.closeChar + self.typed() + self.codewave.brakets
		curClose = self.whithinCloseBounds(self.replacements[0].selections[1].copy().applyOffset(len(self.typed())))
		if curClose:
			repl = util.Replacement(curClose.start, curClose.end, targetText)
			if repl.necessaryFor(self.codewave.editor):
				self.codewave.editor.applyReplacements([repl])
		else:
			self.stop()
	def skipEvent(self):
		return False
	def getSelections(self):
		return [
				self.codewave.editor.getCursorPos(),
				self.replacements[0].selections[1] + len(self.typed())
			]
	def whithinCloseBounds(self,pos):
		for i, repl in enumerate(self.replacements):
			targetPos = self.endPosAt(i)
			next = self.codewave.findNextBraket(targetPos.innerStart)
			if next is not None:
				targetPos.moveSuffix(next)
				if targetPos.innerContainsPos(pos):
					return targetPos
		return False

def newFor(codewave,selections):
	if codewave.editor.allowMultiSelection():
		return ClosingPromp(codewave,selections)
	else:
		return SimulatedClosingPromp(codewave,selections)