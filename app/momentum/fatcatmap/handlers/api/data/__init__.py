import logging
from google.appengine.ext import db

from tipfy import Tipfy

from wirestone.spi.api import MomentumAPIService

QueryParamNames = [('iDisplayStart', int, 'offset'), ('iDisplayLength', int, 'limit'), ('iColumns', int, 'properties'),
					('offset', int, 'offset'), ('limit', int, 'limit'), ('keys_only', bool, 'keys_only')]


class MomentumDataAPIService(MomentumAPIService):
	
	model = None
	query = None
	query_params = {'offset':0, 'limit':25}
	request_params = {}
	request = None
	result = {}
	response = {}
	
	def __init__(self):
		self.request = Tipfy.request
	
	def buildDataAPIResponse(self):
		return self.result

	def buildDataTableResponse(self):
		obj = {'iTotalRecords':self.result['data_count'], 'iTotalDisplayRecords':self.result['data_count'], 'cursor': self.result['cursor'], 'data': self.result['data'], 'query':self.query_params}
		if self.model is not None:
			grid = self.model.generateGrid()
			obj['sColumns'] = grid.getColumnsForRPC()
			obj['gridProto'] = grid.getColumnsForProto()
			obj['modelProto'] = self.model.getProto()
		return obj
		
	
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
			
			## Build response for datagrid if prompted
			if self.request.args.get('mode', False) != False:
				mode = self.request.args.get('mode')
				if mode == 'datagrid':
					return self.buildDataTableResponse()

			return self.buildDataAPIResponse()
			
		else:
			self.result = result

    	return decorated


## Data API Exceptions
class NotFoundError(Exception): pass
class NotLoggedInError(Exception): pass