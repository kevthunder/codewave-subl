import os.path
import imp, sys
import sublime, sublime_plugin

BASE_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path += [BASE_PATH]

import codewave_core.codewave
import codewave_subl_editor
import codewave_core.logger
import codewave_core.storage

def getBufferKey(view) :
	return 'buffer_' + str(view.buffer_id())
	
class CodewaveCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print("run CodewaveCommand")
		global codewaves
		debug = True
		
		if debug :
			# reload
			try :
				for m in sys.modules.values() :
					try :
						if hasattr(m,'__file__') and "codewave" in m.__file__.lower() :
							print("reload :" + m.__name__)
							imp.reload(m)
					except Exception as e:
						print("reload failed :" + str(e))
			except Exception as e:
				print("reloads failed :" + str(e))
			
		if debug or 'codewaves' not in globals() or codewaves is None :
			print('init codewave')
			codewave_core.logger.WRITE_FUNCT = self.printFunct
			codewave_core.storage.CONFIG_FOLDER = os.path.join(sublime.packages_path(), 'Codewave')
			codewave_core.codewave.init()
			
		if 'codewaves' not in globals():
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
		print(txt)

class CodewaveListener(sublime_plugin.EventListener):
	def on_modified(self,view):
		global codewaves
		if 'codewaves' in globals():
			key = getBufferKey(view)
			if key in codewaves :
				cw = codewaves[key]
				if len(cw.editor.changeListeners) :
					view.run_command("codewave_modified",{ "key" : key });
					
class CodewaveModifiedCommand(sublime_plugin.TextCommand):
	def run(self, edit, key):
		if key in codewaves :
			cw = codewaves[key]
			cw.editor.edit = edit
			for callback in cw.editor.changeListeners :
				callback()