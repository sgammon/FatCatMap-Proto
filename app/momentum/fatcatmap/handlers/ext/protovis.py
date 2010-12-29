from momentum.fatcatmap.handlers.ext import OutputPackage


class Protovis(OutputPackage):
	
	@classmethod
	def north(cls):
		html = ["<script type='text/javascript' src='/assets/js/protovis/protovis-d3.2.js'></script>"]
		html.append("<script type='text/javascript' src='/assets/js/grapher/marks-0.1.js'></script>")
		
		return html