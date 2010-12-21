from momentum.fatcatmap.handlers.ext import OutputPackage


class AutoComplete(OutputPackage):
	
	@classmethod
	def north(cls):
		html = ["<link rel='stylesheet' type='text/css' src='/assets/style/autocomplete/facelist-0.1.css' />"]
		html.append("<link rel='stylesheet' type='text/css' src='/assets/style/autocomplete/facelist.ie-0.1.css' />")			
		
		return html
		
	@classmethod
	def south(cls):
		html = []
		html.append("<script type='text/javascript' src='/assets/js/autocomplete/autocomplete.js'></script>")		
		html.append("<script type='text/javascript' src='/assets/js/autocomplete/jquery.autocomplete.js'></script>")		
		html.append("<script type='text/javascript' src='/assets/js/autocomplete/jquery.facelist.js'></script>")
		return html