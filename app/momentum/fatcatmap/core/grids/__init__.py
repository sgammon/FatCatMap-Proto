from tipfy import url_for


class FCMDataGrid(object):

	_endpoint = None
	_method = None
	_method_args = []
	_method_kwargs = {}
	_script_snippets = {'north':None, 'south':None}
	_grid_args = None

	columns = []
	_datatype = 'json'
	

	def __init__(self, config=None, **kwargs):

		self._grid_args = {}
		if config is not None:
			self.set_config(config)
		
		for key, value in kwargs.items():
			self._grid_args[key] = value
		

	def set_config(self, config):
		if 'endpoint' in config: self.set_endpoint(config['endpoint'])
		if 'method' in config: self.set_method(config['method'])
		if 'script_snippet' in config: self.set_script_snippets(config['script_snippet'])
		if 'grid_args' in config: self.set_extra_args(config['grid_args'])
		if 'columns' in config: self.set_columns(config['columns'])
		

	def set_columns(self, columns):
		if columns is not None:
			self.columns = []
			for column in columns:
				self.columns.append(column)
		

	def get_columns(self):
		return self.columns


	def set_endpoint(self, endpoint, **kwargs):
		if 'mode' not in kwargs:
			kwargs['mode'] = 'datagrid'
		self._endpoint = url_for(endpoint, **kwargs)
		

	def set_method(self, method, *args, **kwargs):
		self._method = method
		self._method_args = args
		self._method_kwargs = kwargs
		

	def set_extra_args(self, args):
		self._grid_args = args
		

	def set_script_snippets(self, value1, value2=None):

		if isinstance(value1, tuple):
			self._script_snippets['north'], self._script_snippets['south'] = value1
		else:
			self._script_snippets['north'] = value1
			if value2 is not None:
				self._script_snippets['south'] = value2
		

	def get_script_snippet(self, position):
		if position == 'north':
			if self._script_snippets['north'] is not None:
				return 'snippets/grids/'+self._script_snippets['north']
		elif position == 'south':
			if self._script_snippets['south'] is not None:			
				return 'snippets/grids/'+self._script_snippets['south']
		else: return None
		

	def get_endpoint(self):
		return self._endpoint
		

	def get_method(self):
		
		if len(self._method_args) == 0 and len(self._method_kwargs) == 0:
			return (self._method, {})
		else:
			arg_struct = []
			for arg in self._method_args:
				arg_struct.append((self._method_args.index(arg), self._method_args[arg]))
			for name, value in self._method_kwargs.items():
				arg_struct.append((name, value))
			return (self._method, arg_struct)
		
		
	def get_extra_args(self):
		if self._grid_args is None or len(self._grid_args) == 0:
			return {}
		return self._grid_args
		

	def getColumnsForRPC(self):
		columns = ['key']
		for label, name, args in self.columns:
			columns.append(name)
			
		return ','.join(columns)


	def getColumnsForMacro(self):
		columns = [{'sTitle':'Key','sName':'key','bVisible':False}]
		for label, name, args in self.columns:
			column = {}

			if label is not None:
				column['sTitle'] = label
			if name is not None:
				column['sName'] = name

			if args is not None:
				for key, value in args.items():
					column[key] = args[key]

			columns.append(column)

		return columns

	def getColumnsForProto(self):
		columns = []
		for label, name, args in self.columns:
			column = {'name': name}
			columns.append(name)

		return columns

				

def model_fields_for_grid(model, exclude=None, only=None):
	
	p = model.properties()
	
	if exclude is not None:
		grid_entries = [(f, key) for f, key in p.items() if f not in exclude]
	elif only is not None:
		grid_entries = [(f, key) for f, key in p.items() if f in only]
	else:
		grid_entries = p.items()

	columns = []

	for field_name, field_class in grid_entries:

		if field_class.verbose_name != None:
			label = field_class.verbose_name
		else:
			label = field_name

		columns.append((label, field_name, None))
		
	return columns


def get_model_grid(model, endpoint=None, method=None, exclude=None, only=None, **kwargs):
	
	# Generate form class
	f = type(model.kind() + 'Grid', (FCMDataGrid,), {})()
	f.set_columns(model_fields_for_grid(model, exclude=exclude, only=only))
	
	if len(kwargs) > 0:
		f.set_extra_args(kwargs)
	
	if endpoint is not None and method is not None:
		f.set_endpoint(endpoint)
		f.set_method(method)

	return f