import sublime

class SublEditor():
	def __init__(self,view):
		self.view = view
		self.edit = None
		self.namespace = 'sublime'
	def getCursorPos(self):
		sel = self.view.sel()
		return {'start':sel[0].begin(), 'end':sel[0].end()}
	def textSubstr(self,start,end):
		return self.view.substr(sublime.Region(start, end))
	def textLen(self):
		return self.view.size()
	def insertTextAt(self,text,pos):
		self.view.insert(self.edit, pos, text)
	def setCursorPos(self,start,end = None):
		if end is None :
			end = start
		self.view.sel().clear()
		self.view.sel().add(sublime.Region(start, end))
	def spliceText(self,start, end, text):
		self.view.replace(self.edit, sublime.Region(start, end), text)
	def beginUndoAction(self):
		pass
	def endUndoAction(self):
		pass
	def getLang(self):
		return self.view.settings().get('syntax').split('/').pop().split('.')[0]
	def getEmmetContextObject(self):
		return __import__("emmet-plugin").ctx