import logger
import util

class ClosingPromp():
	def __init__(self,codewave,start,end):
		self.codewave,self.start,self.end = codewave,start,end
		self.len = self.end - self.start
		self.found = False
		self.openBounds = self.closeBounds = None
	def begin(self):
		self.codewave.editor.beginUndoAction()
		self.codewave.editor.insertTextAt("\n"+self.codewave.brakets+self.codewave.closeChar+self.codewave.brakets,self.end)
		self.codewave.editor.insertTextAt(self.codewave.brakets+self.codewave.brakets+"\n",self.start)
		self.codewave.editor.endUndoAction()
		
		self.found = True
		p1 = self.start+len(self.codewave.brakets)
		p2 = self.end+len(self.codewave.brakets)*3+len(self.codewave.closeChar)+2
		self.openBounds = util.wrappedPos(  self.start, p1, p1, p1+len(self.codewave.brakets))
		self.closeBounds = util.wrappedPos( self.end, p2, p2, p2+len(self.codewave.brakets))
		
		self.codewave.editor.setCursorPos(p2)
		# Npp.editor.addSelection(p1,p1)
		# Npp.editor.callback(self.onAddChar, [Npp.SCINTILLANOTIFICATION.CHARADDED])
		return self
	def onAddChar(self,ch):
		# logger.log('added :'+str(ch))
		if ch['ch'] ==  32:
			self.stop()
			self.cleanClose()
	def cleanClose(self):
		if self.updateBounds() :
			closeStr = self.codewave.editor.textSubstr(self.closeBounds.innerStart,self.closeBounds.innerEnd)
			self.codewave.editor.spliceText(self.closeBounds.innerStart,self.closeBounds.innerEnd,closeStr.strip())
			Sels = None # Npp.editor.getSelections()
			for i in reversed(range(0,Sels)):
				s = None # Npp.editor.getSelectionNStart(i)
				e = None # Npp.editor.getSelectionNEnd(i)
				if s >= self.openBounds.innerStart and  s <= self.openBounds.innerEnd :
					self.codewave.editor.setCursorPos(s,e)
	def stop(self):
		if self.codewave.closingPromp == self :
			self.codewave.closingPromp = None
		# Npp.editor.clearCallbacks(self.onAddChar)
		# Npp.editor.clearCallbacks([Npp.SCINTILLANOTIFICATION.CHARADDED])
	def cancel(self):
		if self.updateBounds() :
			self.codewave.editor.beginUndoAction()
			self.codewave.editor.spliceText(self.closeBounds.start-1,self.closeBounds.end,'')
			self.codewave.editor.spliceText(self.openBounds.start,self.openBounds.end+1,'')
			self.codewave.editor.endUndoAction()
		
			self.codewave.editor.setCursorPos(self.start,self.end)
		self.stop()
	def updateBounds(self):
		self.found = False
		self.openBounds = self.whithinOpenBounds(self.start+len(self.codewave.brakets))
		if self.openBounds is not None :
			self.closeBounds = self.whithinCloseBounds(self.openBounds)
			if self.closeBounds is not None :
				self.found = True
		return self.found;
	def whithinOpenBounds(self,pos):
		innerStart = self.start+len(self.codewave.brakets)
		if self.codewave.findPrevBraket(pos) == self.start and self.codewave.editor.textSubstr(self.start,innerStart) == self.codewave.brakets :
			innerEnd = self.codewave.findNextBraket(innerStart)
			if innerEnd is not None :
				return util.wrappedPos( self.start, innerStart, innerEnd, innerEnd+len(self.codewave.brakets))
	def whithinCloseBounds(self,openBounds):
		start = openBounds.end+self.len+2
		innerStart = start+len(self.codewave.brakets)+len(self.codewave.closeChar)
		if self.codewave.editor.textSubstr(start,innerStart) == self.codewave.brakets+self.codewave.closeChar :
			innerEnd = self.codewave.findNextBraket(innerStart)
			if innerEnd is not None :
				return util.wrappedPos( start, innerStart, innerEnd, innerEnd+len(self.codewave.brakets))