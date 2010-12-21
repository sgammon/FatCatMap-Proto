from momentum.fatcatmap.handlers.ext import OutputPackage


class Plupload(OutputPackage):
	
	@classmethod
	def north(cls):
		html = ["<link href='/assets/style/plupload/queue-widget-0.1.css' rel='stylesheet' type='text/css' />"]
		html.append("<script type='text/javascript' src='/assets/js/plupload/gears-init.js'></script>")
		html.append("<script type='text/javascript' src='http://bp.yahooapis.com/2.4.21/browserplus-min.js'></script>")
		html.append("<script type='text/javascript' src='/assets/js/plupload/plupload.full.min.js'></script>")
		html.append("<script type='text/javascript' src='/assets/js/plupload/jquery.plupload.queue.min.js'></script>")
		html.append("<script type='text/javascript' src='/assets/js/plupload/util.upload.0.1.js'></script>")
		
		return html