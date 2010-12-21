from momentum.fatcatmap.handlers.ext import OutputPackage


class DataGrid(OutputPackage):
	
	@classmethod
	def north(cls):
		html = []
		html.append("<link rel='stylesheet' href='/assets/style/datagrid/demo_page.css' type='text/css' media='screen' />")
		html.append("<link rel='stylesheet' href='/assets/style/datagrid/demo_table.css' type='text/css' media='screen' />")
		
		return html
		
	@classmethod
	def south(cls):
		html = ["<script type='text/javascript' src='/assets/js/datagrid/jquery.dataTables.min.js'></script>"]
		html.append("<script type='text/javascript' src='/assets/js/datagrid/util.datagrid.0.1.js'></script>")
		return html