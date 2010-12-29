import config
import logging
import simplejson

from tipfy import Response
from tipfy import import_string
from tipfy import cached_property
from tipfy.ext.jsonrpc import JSONRPCMixin

from lovely.jsonrpc.dispatcher import JSONRPCDispatcher

from momentum.fatcatmap.handlers import BaseFCMRequestHandler
from momentum.fatcatmap.core.data.encode import FCMJSONEncoder


class MomentumAPIDispatcher(BaseSPIRequestHandler, JSONRPCMixin):

	jsonrpc_service = None

	def dispatchAPICall(self, module, service, method, format, http_method):
		
		## @TODO: Add error checking here
		api_module = import_string('.'.join(['momentum','fatcatmap','api', module, service, service+'Service']))()

		## Debug logging
		do_log = False
		if self.apiConfig['debug'] == True: do_log = True
		if do_log:
			logging.info('=============== API DISPATCHER ===============')
			logging.info('--Module: '+str(module))
			logging.info('--Service: '+str(service))
			logging.info('--Method: '+str(method))
			logging.info('--Format: '+str(format))
			logging.info('--HTTP Method: '+str(http_method))
			logging.info('--Request Data: '+str(self.request.data))
		
		if method is None:
			if format == 'json':
				
				if do_log: logging.info('=== ACTION IS JSONRPC. BEGINNING ACTION ===')
				
				## Set JSONRPC params
				self.jsonrpc_service = api_module
				
				if do_log:
					logging.info('--Service: '+str(self.jsonrpc_service))
					logging.info('--Name: '+str(self.jsonrpc_name))
					logging.info('--Summary: '+str(self.jsonrpc_summary))
					logging.info('=== RUNNING DISPATCHER ===')
				
				res = self.json_rpc_dispatcher.dispatch(self.request.data)
				
				if do_log:
					logging.info('--Result: '+str(res))
					logging.info('Finished request. Responding.')
				
				return Response(FCMJSONEncoder().encode(res), mimetype='application/json')
			else:
				return Response('<b>Given format not supported.</b>')
		else:
			res = getattr(api_module, method)()
			if format == 'json':
				return Response(res, mimetype='application/json')
				
	@cached_property
	def json_rpc_dispatcher(self):
		return JSONRPCDispatcher(instance=self.jsonrpc_service,
								 name=self.jsonrpc_name,
								 summary=self.jsonrpc_summary,
								 help=self.jsonrpc_help,
								 address=self.jsonrpc_address,
								 json_impl=SPIJSONEncoder)
								
				
	@cached_property
	def apiConfig(self):
		return config.config.get('wirestone.spi.api')

		
	# =============== MAP HTTP METHODS TO DISPATCHER =============== #
	def get(self, module, service=None, method=None, format='json'):
		return self.dispatchAPICall(module, service, method, format, 'GET')
		
	def post(self, module, service=None, method=None, format='json'):
		return self.dispatchAPICall(module, service, method, format, 'POST')
		
	def put(self, module, service=None, method=None, format='json'):
		return self.dispatchAPICall(module, service, method, format, 'PUT')
		
	def delete(self, module, service=None, method=None, format='json'):
		return self.dispatchAPICall(module, service, method, format, 'DELETE')
		
	def options(self, module, service=None, method=None, format='json'):
		return self.dispatchAPICall(module, service, method, format, 'OPTIONS')
		
	def head(self, module, service=None, method=None, format='json'):
		return self.dispatchAPICall(module, service, method, format, 'HEAD')
		
	def trace(self, module, service, method=None, format='json'):
		return self.dispatchAPICall(module, service, method, format, 'TRACE')