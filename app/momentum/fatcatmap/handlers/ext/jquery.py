from momentum.fatcatmap.handlers.ext import OutputPackage


class jQuery(OutputPackage):
	
	@classmethod
	def north(cls):
		html = ["<link type='text/css' href='/assets/style/jquery/ui/dark-v2/jquery-ui-1.8.7.custom.css' rel='stylesheet' />"]
		html.append("<script type='text/javascript' src='/assets/js/jquery/jquery-1.4.4.min.js'></script>")
		html.append("<script type='text/javascript' src='/assets/js/jquery/ui/jquery-ui-1.8.7.custom.min.js'></script>")		
		html.append("<script type='text/javascript' src='/assets/js/jquery/jquery.rpc.js'></script>")
		
		return html