from momentum.fatcatmap.handlers.ext import OutputPackage


class Protovis(OutputPackage):
	
	@classmethod
	def north(cls):
		html = ["<script type='text/javascript' src='/assets/js/protovis/protovis-r3.2.js'></script>"]
		
		return html