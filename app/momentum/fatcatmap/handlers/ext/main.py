from momentum.fatcatmap.handlers.ext import OutputPackage


class Main(OutputPackage):
	
	@classmethod
	def north(cls):
		html = ["<link rel='stylesheet' media='screen' href='/assets/style/main-0.1.css' />"]
		return html
		
		
class Forms(OutputPackage):

	@classmethod
	def north(cls):
		html = ["<link rel='stylesheet' media='screen' href='/assets/style/forms-0.1.css' />"]
		return html