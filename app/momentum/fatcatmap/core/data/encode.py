import logging

from simplejson import JSONEncoder
from simplejson import JSONDecoder

from google.appengine.ext import db


def encodeKey(key, stop=False):
	
	'''
	
	Encodes an App Engine Datastore key to JSON.
	
	Structure:
		--value: string representation of key
		--kind: kind name of the object the key represents
		--name: key name for key (defaults to 'null')
		--id: sequential ID assigned by the datastore (defaults to 'null')
		--parent: parent record (defaults to 'null')
			NOTE: if a parent is found, this function will encode that key, too.
				  if the parent of a given key has a parent, it is represented
				  with a string to avoid too much recursion.
		--namespace: the multitenancy namespace given to a key
		
	'''
	
	key_dict = {'value': str(key), 'kind': key.kind(), 'name': None, 'id': None, 'parent': None, 'namespace': None}
	if key.name() is not None:
		key_dict['name'] = key.name()
	else:
		key_dict['id'] = key.id()
	if key.parent() is not None:
		if stop is not False:
			key_dict['parent'] = encodeKey(key.parent(), True)
		else:
			key_dict['parent'] = str(key.parent())
	key_dict['namespace'] = key.namespace()
	
	return key_dict
	
	
def convertPropValue(model, prop, prop_class, stop=False):
	
	if getattr(model, prop) is not None:
		if prop_class in ['ReferenceProperty', 'SelfReferenceProperty']:
			if stop is False:
	 			return encodeModel(getattr(model, prop))
			else:
				return encodeKey(getattr(model, prop).key())
				
		elif prop_class == 'BlobReferenceProperty':
			return {'value': str(getattr(model, prop).key())}
			
		elif prop_class in ['DateTimeProperty', 'DateProperty', 'TimeProperty']:
			return str(getattr(model, prop))
		
	return getattr(model, prop)
	

def encodeModel(model, stop=False):
	
	'''
	
	Encodes an App Engine Datastore model to JSON.
	
	Structure:
		--key: encoded key of model (see function: encodeKey)
		--properties: dict of model property classes and values (dict key is prop name)
			--class: string representation of property implementation class
			--value: actual value of property
	
	'''
	
	model_dict = {'key':encodeKey(model.key()), 'properties':{}}
	properties = model.properties()
	if isinstance(model, db.Expando):
		properties = properties+model.dynamic_properties()
	
	for prop in properties:
		prop_class = properties[prop].__class__.__name__
		model_dict['properties'][prop] = convertPropValue(model, prop, prop_class, stop)
	return model_dict
	
		

class FCMJSONEncoder(JSONEncoder):
	
	def default(self, o):
				
		if isinstance(o, (db.Model, db.Key)):
			if isinstance(o, db.Key): return encodeKey(o)
			elif isinstance(o, db.Model): return encodeModel(o)
		else:
			return JSONEncoder().encode(o)
						
	def decode(self, o):
		return JSONDecoder().decode(o)
		
	def dumps(self, o):
		return self.encode(o)