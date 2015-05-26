import codewave_core.util as util

class Editor(object):
	def __init__(self):
		self.namespace = None
		self._lang = None
		
	def bindedTo(self,codewave):
		pass

	@property
	def text(self):
		raise NotImplementedError
	@text.setter
	def text(self, val):
		raise NotImplementedError
	def textCharAt(self,pos):
		raise NotImplementedError
	def textLen(self):
		raise NotImplementedError
	def textSubstr(self,start, end):
		raise NotImplementedError
	def insertTextAt(self,text, pos):
		raise NotImplementedError
	def spliceText(self,start, end, text):
		raise NotImplementedError
	def getCursorPos(self):
		raise NotImplementedError
	def setCursorPos(self,start, end = None):
		raise NotImplementedError
	def beginUndoAction(self):
		pass
	def endUndoAction(self):
		pass
	def getLang(self):
		return self._lang
	def setLang(self,val):
		self._lang = val
	def getEmmetContextObject(self):
		return None
	def allowMultiSelection(self):
		return False
	def setMultiSel(self,selections):
		raise NotImplementedError
	def getMultiSel(self):
		raise NotImplementedError
	def canListenToChange(self):
		return False
	def addChangeListener(self,callback):
		raise NotImplementedError
	def removeChangeListener(self,callback):
		raise NotImplementedError
	
	def getLineAt(self,pos):
		return util.Pos(self.findLineStart(pos),self.findLineEnd(pos))
	def findLineStart(self,pos):
		p = self.findAnyNext(pos ,["\n"], -1)
		return p.pos+1 if p is not None else 0
	def findLineEnd(self,pos): 
		p = self.findAnyNext(pos ,["\n","\r"])
		return p.pos if p is not None else self.textLen()
 
	def findAnyNext(self,start,strings,direction = 1):
		if direction > 0:
			text = self.textSubstr(start,self.textLen())
		else:
			text = self.textSubstr(0,start)
		bestPos = bestStr = None
		for stri in strings:
			pos = text.find(stri) if direction > 0  else text.rfind(stri)
			if pos != -1:
				if not bestPos is not None or bestPos*direction > pos*direction:
					bestPos = pos
					bestStr = stri
		if bestStr is not None:
			return util.StrPos((bestPos + start if direction > 0 else bestPos),bestStr)
		return None
	def applyReplacements(self,replacements):
		selections = []
		offset = 0
		for repl in replacements:
			repl.withEditor(self)
			repl.applyOffset(offset)
			repl.apply()
			offset += repl.offsetAfter()
			
			selections += repl.selections
		self.applyReplacementsSelections(selections)
			
	def applyReplacementsSelections(self,selections):
		if len(selections) > 0:
			if self.allowMultiSelection():
				self.setMultiSel(selections)
			else:
				self.setCursorPos(selections[0].start,selections[0].end)