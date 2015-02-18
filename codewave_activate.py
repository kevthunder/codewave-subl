import os.path
import codewave.codewave
import codewave_subl_editor
import codewave.logger
import codewave.storage


import sublime, sublime_plugin

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
			
		key = 'buffer_' + str(self.view.buffer_id())
		if key in codewaves :
			cw = codewaves[key]
		else :
			cw = codewave.codewave.Codewave(codewave_subl_editor.SublEditor(self.view))
			# codewaves[key] = cw
		cw.editor.edit = edit
		cw.onActivationKey()
		
	def printFunct(self,txt):
		print txt

