from momentum.fatcatmap.handlers.ext import OutputPackage


class jQuery(OutputPackage):
	
	@classmethod
	def north(cls):
		html = ["<script type='text/javascript' src='/assets/js/jquery/jquery-1.4.4.min.js'></script>"]
		html.append("<script type='text/javascript' src='/assets/js/jquery/jquery.rpc.js'></script>")
		
		return html