import os.path
import codewave.codewave
import codewave_subl_editor
import codewave.logger
import codewave.storage


import sublime, sublime_plugin

def getBufferKey(view) :
	return 'buffer_' + str(view.buffer_id())
	
class CodewaveCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print 'run CodewaveCommand'
		global codewaves
		debug = True
		
		if debug :
			# reload
			try :
				reload(codewave.codewave)
				reload(codewave_subl_editor)
				reload(codewave.logger)
				reload(codewave.storage)
			except:
				print "reload failed"
			
		if debug or 'codewaves' not in vars() or codewaves is None :
			print 'init codewave'
			codewave.logger.WRITE_FUNCT = self.printFunct
			codewave.storage.CONFIG_FOLDER = os.path.join(sublime.packages_path(), 'Codewave')
			codewave.codewave.init()
			codewaves = {}
			
		key = getBufferKey(self.view)
		if key in codewaves :
			cw = codewaves[key]
		else :
			cw = codewave.codewave.Codewave(codewave_subl_editor.SublEditor(self.view))
			codewaves[key] = cw
		cw.editor.edit = edit
		cw.onActivationKey()
		
	def printFunct(self,txt):
		print txt

class GoogleAutocomplete(sublime_plugin.EventListener):
	def on_modified(self,view):
		global codewaves
		key = getBufferKey(view)
		if key in codewaves :
			cw = codewaves[key]
			for callback in cw.editor.changeListeners :
				callback()