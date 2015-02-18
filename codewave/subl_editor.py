import sublime

class SublEditor():
	def __init__(self,view):
		self.view = view
		self.namespace = 'sublime'
	def getCursorPos(self):
		sel = self.view.sel()
		return {'start':sel[0].begin(), 'end':sel[0].end()}
	def textSubstr(self,start,end):
		return None # Npp.editor.getTextRange(start,end)
	def textLen(self):
		return None # Npp.editor.getLength()
	def insertTextAt(self,text,pos):
		# Npp.editor.insertText(pos,text)
	def setCursorPos(self,start,end = None):
		if end is None :
			end = start
		# Npp.editor.setSelection(start,end)
	def spliceText(self,start, end, text):
		# Npp.editor.setTarget(start, end)
		# Npp.editor.replaceTarget(text)
	def beginUndoAction(self):
		# Npp.editor.beginUndoAction()
	def endUndoAction(self):
		# Npp.editor.endUndoAction()
	def getLang(self):
		return None #Npp.notepad.getCurrentLang().name