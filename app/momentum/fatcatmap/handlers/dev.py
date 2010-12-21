from momentum.fatcatmap.handlers import FCMRequestHandler


class SandboxIndex(FCMRequestHandler):
	
	def get(self):
		
		return self.render('sandbox/main.html', dependencies=['Protovis'])