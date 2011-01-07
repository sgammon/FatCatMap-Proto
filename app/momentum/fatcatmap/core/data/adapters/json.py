import uuid
import logging

from google.appengine.api import memcache
from google.appengine.ext import blobstore

from django.utils.simplejson import JSONEncoder
from django.utils.simplejson import JSONDecoder

from google.appengine.ext import db

from momentum.fatcatmap.core.data import MomentumDataAdapter

model_cache = {}


#### ==== KEY FUNCTIONS ==== ####
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

	key_dict = {'value': str(key), 'kind': key.kind(), 'name': None, 'id': None, 'parent': None, 'namespace': None, '_pc_type':'KEY'}
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


def decodeKey(key):

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

	return db.Key(key['value'])


#### ==== MODEL FUNCTIONS ==== ####
def convertPropValueToJSON(model, prop, prop_class, stop=False):

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

	else:
		return getattr(model, prop)


def encodeModel(model, stop=False):

	'''

	Encodes an App Engine Datastore model to JSON.

	Structure:
		--key: encoded key of model (see function: encodeKey)
		--class: dict describing the class structure
			--path: a python path to the model (e.x. momentum.fatcatmap.models.graph.Node)
			--type: class name of the model - Model, PolyPro or Expando
			--ancestry: describes a polymodel's ancestry
		--properties: dict of model property classes and values (dict key is prop name)
			--class: string representation of property implementation class
			--value: actual value of property

	'''

	model_dict = {'key':encodeKey(model.key()), 'class':{'path':model._getModelPath(), 'type':model.__class__.__name__, 'ancestry':model._getClassPath()}, 'properties':{}, '_pc_type':'MODEL'}
	properties = model.properties()
	if isinstance(model, db.Expando):
		properties = properties+model.dynamic_properties()

	for prop in properties:
		prop_class = properties[prop].__class__.__name__
		model_dict['properties'][prop] = convertPropValueToJSON(model, prop, prop_class)

	cache_hint = str(uuid.uuid4())
	model_dict['_pc_cache_hint'] = cache_hint

	cache_key = 'KEY::'+str(model.key())+'::'+cache_hint
	logging.info('JSON TRANSPORT CACHE: Storing model '+str(model)+' at memcache location "'+cache_key+'".')
	global model_cache
	model_cache[cache_key] = model
	memcache.set(cache_key, model, time=3600)

	return model_dict


def decodeModel(model, stop=False):

	'''

	Encodes an App Engine Datastore model to JSON.

	Structure:
		--key: encoded key of model (see function: encodeKey)
		--properties: dict of model property classes and values (dict key is prop name)
			--class: string representation of property implementation class
			--value: actual value of property

	'''

	global model_cache

	## Encode key first...
	decoded_key = model['key']

	## Grab by cache hint...
	if '_pc_cache_hint' in model:

		cache_key = 'KEY::'+str(decoded_key)+'::'+model['_pc_cache_hint']

		logging.info('JSON TRANSPORT CACHE: Retrieving cache object at location "'+cache_key+'".')

		if cache_key in model_cache:
			return model_cache[cache_key]

		else:
			obj = memcache.get(cache_key)
			if obj is not None:
				logging.info('JSON TRANSPORT CACHE: Returning memcache object "'+str(obj)+'".')
				return obj

			logging.error('JSON TRANSPORT CACHE: Cache miss. Failing. Your mileage may vary from here...')

	else:
		model_impl_class = __import__('.'.join(key['class']['path'])[0:-1], globals(), locals(), '.'.join(key['class']['path'])[-1])
		model_impl_class = getattr(model_impl_class, '.'.join(key['class']['path'])[-1])

		## Create object...
		model_impl_obj = model_impl_class(key=decoded_key)

		for prop, prop_obj in key['properties'].items():
			setattr(model_impl_obj, prop, convertPropValueFromJSON(model_impl_class, prop, prop_obj))

		return model_impl_obj


#### ==== Encoder/Decoder Adapters ==== ####
class FCMJSONAdapter(MomentumDataAdapter):

	@classmethod
	def dumps(cls, o, *args, **kwargs):
		return FCMJSONEncoder(*args, **kwargs).encode(o)

	@classmethod
	def loads(cls, o, *args, **kwargs):
		return FCMJSONDecoder(*args, **kwargs).decode(o)

	@classmethod
	def encode(cls, *args, **kwargs):
		return FCMJSONEncoder().encode(*args, **kwargs)

	@classmethod
	def decode(cls, *args, **kwargs):
		return FCMJSONDecoder().decode(*args, **kwargs)


class FCMJSONEncoder(JSONEncoder):

	def default(self, o):

		if isinstance(o, (db.Model, db.Key)):
			if isinstance(o, db.Key):
				return encodeKey(o)
			elif isinstance(o, db.Model):
				return encodeModel(o)
		else:
			return JSONEncoder().encode(o)

	def decode(self, o):
		return FCMJSONDecoder().decode(o)


class FCMJSONDecoder(JSONDecoder):

	def __init__(self, *args, **kwargs):
		super(FCMJSONDecoder, self).__init__('utf-8', object_hook=self._pc_decode, *args, **kwargs)

	@classmethod
	def _pc_decode(cls, o):

		if '_pc_type' in o:
			if o['_pc_type'].lower() == 'key':
				return decodeKey(o)
			if o['_pc_type'].lower() == 'model':
				return decodeModel(o)
		return o

	def encode(self, o):
		return FCMJSONEncoder().encode(o)
