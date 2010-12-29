from momentum.fatcatmap.handlers import FCMRequestHandler


class AdminIndex(FCMRequestHandler):
	
	def get(self):
		return self.response('<b>AdminIndex</b>')