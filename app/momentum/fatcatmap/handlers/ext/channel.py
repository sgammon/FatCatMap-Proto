from momentum.fatcatmap.handlers.ext import OutputPackage


class Protovis(OutputPackage):
	
	@classmethod
	def north(cls):
		html = ["<script src='/_ah/channel/jsapi'></script>"]
		
		return html