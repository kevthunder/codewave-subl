
class Detector():
	def __init__(self,data={}):
		self.data = data
	def detect(self,finder):
		if self.detected(finder):
			if self.data['result'] is not None:
				return self.data['result']
		else:
			if self.data['else'] is not None:
				return self.data['else'] 
	def detected(self,finder):
		pass


class LangDetector(Detector):
	def detect(self,finder):
		if finder.codewave is not None :
			lang = finder.codewave.editor.getLang()
			if lang is not None :
				return lang.lower()

class PairDetector(Detector):
	def detected(self,finder):
		if self.data['opener'] is not None and self.data['closer'] is not None and finder.instance is not None:
			pair =  util.Pair(self.data['opener'], self.data['closer'], self.data)
			if pair.isWapperOf(finder.instance.getPos(), finder.codewave.editor.text):
				return True
		return False