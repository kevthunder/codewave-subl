
class Detector():
	def __init__(self,data={}):
		self.data = data
	def detect(self,finder):
		pass
		

class LangDetector(Detector):
	def detect(self,finder):
		if finder.codewave is not None :
			return finder.codewave.editor.getLang().lower()