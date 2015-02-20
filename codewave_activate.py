import os.path
import sublime, sublime_plugin

import codewave_core.codewave
import codewave_subl_editor
import codewave_core.logger
import codewave_core.storage

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
				reload(codewave_core.codewave)
				reload(codewave_subl_editor)
				reload(codewave_core.logger)
				reload(codewave_core.storage)
			except:
				print "reload failed"
			
		if debug or 'codewaves' not in vars() or codewaves is None :
			print 'init codewave'
			codewave_core.logger.WRITE_FUNCT = self.printFunct
			codewave_core.storage.CONFIG_FOLDER = os.path.join(sublime.packages_path(), 'Codewave')
			codewave_core.codewave.init()
			codewaves = {}
			
		key = getBufferKey(self.view)
		if key in codewaves :
			cw = codewaves[key]
		else :
			cw = codewave_core.codewave.Codewave(codewave_subl_editor.SublEditor(self.view))
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