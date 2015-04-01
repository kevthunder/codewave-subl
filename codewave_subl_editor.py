import sublime
import codewave_core.editor
import codewave_core.util

class SublEditor(codewave_core.editor.Editor):
	def __init__(self,view):
		self.view = view
		self.edit = None
		self.namespace = 'sublime'
		self.changeListeners = []
	@property
	def text(self):
		return self.view.substr(sublime.Region(0, self.view.size()))
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
		module = __import__("emmet-plugin")
		if not module.ctx :
			module.init()
		return module.ctx
	def allowMultiSelection(self):
		return True
	def setMultiSel(self,selections):
		self.view.sel().clear()
		for sel in selections :
			self.view.sel().add(sublime.Region(sel.start, sel.end))
	def getMultiSel(self):
		selections = []
		for sel in self.view.sel() :
			selections.append(codewave_core.util.Pos(sel.begin(), sel.end()))
		return selections
	def canListenToChange(self):
		return True
	def addChangeListener(self,callback):
		self.changeListeners.append(callback)
	def removeChangeListener(self,callback):
		self.changeListeners.remove(callback)