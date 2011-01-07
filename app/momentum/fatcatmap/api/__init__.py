import config


_CHESHIRE_TRANSPORT_VERSION = 1.0


## Momentum API Module
class MomentumAPI(object):
	pass


## Request Message
class MomentumAPIRequest(object):

	id = None
	version = 0
	method = None
	client = {}
	params = {}
	opts = {}

	@classmethod
	def spawnRequest(cls, config, adapter):

		raw_request = {'request':{}}

		if 'payload' in config:
			payload = config['payload']

			try:
				raw_request = adapter.decode(payload)
			except:
				pass

		elif 'method_path' in config:
			raw_request['method'] = config['method_path'].split('/')

		request_obj = MomentumAPIRequest()
		if 'id' in raw_request: request_obj.id = raw_request['id']
		if 'version' in raw_request: request_obj.version = raw_request['version']
		if 'request' in raw_request:
			if 'method' in raw_request['request']: request_obj.method = raw_request['request']['method']
			if 'params' in raw_request['request']: request_obj.params = raw_request['request']['params']
			if 'opts' in raw_request['request']: request_obj.opts = raw_request['request']['opts']
		if 'client' in raw_request: request_obj.client = raw_request['client']

		return raw_request


## Response Message
class MomentumAPIResponse(object):

	id = 0
	status = None
	error = False
	result = {}
	request_id = 0
	type = 'BaseResponse'
	platform = {}

	def __init__(self, **kwargs):
		platform_config = config.config.get('momentum.fatcatmap')

		self.platform['name'] = platform_config['name']
		self.platform['version'] = str(platform_config['version_major'])+'.'+str(str(platform_config['version_minor']))+'.'+str(platform_config['version_micro'])+' '+platform_config['version_phase']
		self.platform['debug'] = False

		if 'echo' in kwargs: self.platform['echo'] = kwargs['echo']
		if 'debug' in kwargs: self.platform['debug'] = kwargs['debug']


	@classmethod
	def createSuccessResponse(cls, result):
		pass


	@classmethod
	def createErrorResponse(cls, code, message):
		pass


## GQL or db.Query Responder
def QueryResponder(func):

	def decorated(self, query={}, *args, **kwargs):

		## Add GET and POST params to request params field
		for key, value in self.request.args.items(): self.request_params[key] = value
		for key, value in self.request.form.items(): self.request_params[key] = value

		## Generate query parameters
		for q_param_name, q_param_value in [(q_param_name, converter(self.request_params[key])) for key, converter, q_param_name in QueryParamNames if key in dict(self.request_params.items()+query.items())]:
			self.query_params[q_param_name] = q_param_value

		## Get result of function call
		result = func(self, *args, **kwargs)

		## If it's a query, fetch results according to params and return
		if isinstance(result, (db.Query)):

			if 'keys' in self.query_params and self.query_params['keys'] == 'true':
				result.keys_only = True

			self.result['data_count'] = result.count()
			self.result['data'] = result.fetch(self.query_params['limit'] or 50, self.query_params['offset'] or 0)
			self.result['cursor'] = result.cursor()

			return self.createSuccessResponse()

		else:
			self.result = result

		return decorated