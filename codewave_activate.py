# reload
import codewave.codewave
import codewave.subl_editor
import codewave.logger



import sublime, sublime_plugin

class CodewaveCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		print 'run CodewaveCommand'
		global codewaves
		debug = True
		
		if debug :
			reload(codewave.codewave)
			reload(codewave.subl_editor)
			reload(codewave.logger)
			
		if debug or 'codewaves' not in vars() or codewaves is None :
			print 'init codewave'
			codewave.codewave.init()
			codewaves = {}
			
		key = 'buffer_' + str(self.view.buffer_id())
		if key in codewaves :
			cw = codewaves[key]
		else :
			cw = codewave.codewave.Codewave(codewave.subl_editor.SublEditor(self.view))
			# codewaves[key] = cw
		cw.onActivationKey()

