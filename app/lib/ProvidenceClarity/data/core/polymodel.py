import os
import sys
import logging

from google.appengine.ext import db
from google.appengine.api import datastore
from ProvidenceClarity.data.core.model import ProvidenceClarityModel
from ProvidenceClarity.data.core.properties.polymodel import _ClassKeyProperty
from ProvidenceClarity.data.core.properties.polymodel import _ModelPathProperty

_LOG_IMPORTS = True
_PATH_SEPERATOR = ':'
_KEY_NAME_SEPERATOR = '//'

_PATH_KEY_PROPERTY	= '_path_'
_CLASS_KEY_PROPERTY = '_class_'

_class_map = {}


## +=+=+ Metaclass controlling the creation of Providence/Clarity polymodel objects.
class PolymorphicModel(db.PropertiedClass):

	""" Populates properties like __root_class__ and __class_hierarchy__ and enforces logic about direct instantiation. """

	def __init__(cls, name, bases, dct):
			
		if name == 'PolyModel':
			super(PolymorphicModel, cls).__init__(name, bases, dct, map_kind=False)
			return

		elif PolyModel in bases:
			if getattr(cls, '__class_hierarchy__', None):
				raise db.ConfigurationError(('%s cannot derive from PolyModel as '
				'__class_hierarchy__ is already defined.') % cls.__name__)
			cls.__class_hierarchy__ = [cls]
			cls.__root_class__ = cls
			super(PolymorphicModel, cls).__init__(name, bases, dct)
			
		else:
			super(PolymorphicModel, cls).__init__(name, bases, dct, map_kind=False)

			cls.__class_hierarchy__ = [c for c in reversed(cls.mro())
				if issubclass(c, PolyModel) and c != PolyModel]

			if cls.__class_hierarchy__[0] != cls.__root_class__:
				raise db.ConfigurationError(
					'%s cannot be derived from both root classes %s and %s' %
					(cls.__name__,
					cls.__class_hierarchy__[0].__name__,
					cls.__root_class__.__name__))

		_class_map[cls.class_key()] = cls
		
			
## +=+=+ Customized polymorphic database model based on Google's PolyModel implementation.
class PolyModel(Model):
	"""
	
	Description: A modification to Model designed to introduce polymorphism,
	allowing models to inherit properties and methods from other models.
	Cannot be instantiated directly - designed only to be extended.
	
	Abstract: Once a model is created that extends PolyModel, other models
	can be created that extend the original. In Providence/Clarity, all
	polymorphic types eventually extend the 'E' model (for "Entity").
	
	Example:
	
		-----
		| E |
		-----
		  |
		  ---------------------------------
			 |				 |			  |
		-----------		  --------		 ----------
		| GeoArea |		  | Role |		 | Person |
		-----------		  --------		 ----------
			 |				  |
			 |				  |
		------------		  ---------------------
		| US State |			  |				  |
		------------		--------------	-------------
							| Legislator |	| President |
							--------------	-------------
								   |
							---------------
							|			  |
						-----------	 ---------------	 
						| Senator |	 | Congressman |
						-----------	 ---------------

	When a PolyModel object is constructed, there are two special properties
	that are automatically set: _class_key_ (list) and _class_path_ (str).
	The class key describes the object's ancestry, and the class path stores
	the python module path to the corresponding class. For example, let's
	create an object of kind "Senator":
	
		s = Senator(prop1='string',prop2=123)
		s.put()
		
		## values of special props
		
		print s._class_key_
		>> ('E','Role','Legislator','Senator')
		
		print s._class_path_
		>> ('data','entities','people','Senator')
		
	Since we store the class path along with the class key, PolyModel can
	lazy-load the implementation class when an entity is pulled from the
	datastore:
	
		q = E.all()
		r = q.fetch(50)
		
	... will automatically import each implementation class as it returns
	fetched results.

	"""

	__metaclass__ = PolymorphicModel

	## stores class inheritance/ancestry (list property)
	_class_property = _ClassKeyProperty(name=_CLASS_KEY_PROPERTY)
	
	## stores python package import path
	_model_path_property = _ModelPathProperty(name=_PATH_KEY_PROPERTY,indexed=False)

	
	def __new__(cls, *args, **kwds):
		""" Prevents direct instantiation of PolyModel. """
		if cls is PolyModel:
			raise NotImplementedError() # raise NotImplemented
		return super(PolyModel, cls).__new__(cls, *args, **kwds)
		
		
	def __init__(self, *args, **kwargs):
		""" Namespaces a given key_name with the kind name prefixed. """
		
		logging.info('Initiating new PolyModel object...')
		
		# Only namespace keyname if entity is not a root polymodel type
		if len(self.class_key_as_list()) > 1:
			
			logging.info('Not a root Poly... namespacing keyname...')
			
			if '_derived_key_name' in kwargs and kwargs['_derived_key_name'] != True:

				logging.info('No derived key to take from.')

				if 'key_name' in kwargs:

					logging.info('Derived: '+str(self._getNamespacedKeyName(kwargs['key_name'])))
					kwargs['key_name'] = self._getNamespacedKeyName(kwargs['key_name'])
					
			else:
				if 'key_name' in kwargs:
					logging.info('Derived: '+str(self._getNamespacedKeyName(kwargs['key_name'])))
					kwargs['key_name'] = self._getNamespacedKeyName(kwargs['key_name'])
				
		else:
			logging.info('This is a root polymodel. No namespaced keyname then, moving on...')
				
		super(PolyModel, self).__init__(*args, **kwargs)
		

	@classmethod
	def kind(cls):
		""" Always return name of root class. """		 
		if cls.__name__ == 'PolyModel': return cls.__name__
		else: return cls.class_key()[0]
		

	@classmethod
	def class_key(cls):
		""" Returns class path (in tuple form). """
		if not hasattr(cls, '__class_hierarchy__'):
			raise NotImplementedError('Cannot determine class key without class hierarchy')
		return tuple(cls.class_name() for cls in cls.__class_hierarchy__)


	@classmethod
	def class_name(cls):
		""" Returns the name of the current class. """
		return cls.__name__

	
	@classmethod
	def path_key(cls):
		""" Returns the Python import path for the implementation class (in tuple form). """
		if not hasattr(cls, _PATH_KEY_PROPERTY):
			return tuple(i for i in str(cls.__module__+'.'+cls.__name__).split('.'))
		else:
			path_t = getattr(cls, _PATH_KEY_PROPERTY).split(_PATH_SEPERATOR)
			return tuple('.'.join(path_t).split('.'))

	
	def path_module(self):
		""" Returns the module part of the Python import path for the implementation class (in tuple form). """
		if not hasattr(self, _PATH_KEY_PROPERTY):
			return tuple(self.__module__.split('.'))
		else:
			path_t = getattr(self, _PATH_KEY_PROPERTY).split(_PATH_SEPERATOR)
			return tuple(path_t[0].split('.'))


	def path_module_name(self):
		""" Returns the module part of the Python import path for the implementation class (in string form). """
		if not hasattr(self, _PATH_KEY_PROPERTY):
			return str(self.__module__)
		else:
			path_t = getattr(self, _PATH_KEY_PROPERTY).split(_PATH_SEPERATOR)
			return path_t[0]

			
	@classmethod
	def path_class(cls):
		""" Returns a Python 'class' object of the implementation class. """
		if _class_map[cls.class_key()] is not None:
			return _class_map[cls.class_key()]
		else: return cls
		

	@classmethod
	def from_entity(cls, entity):

		if(_PATH_KEY_PROPERTY in entity and
		   tuple(entity[_PATH_KEY_PROPERTY]) != cls.path_key()):
			key = entity[_PATH_KEY_PROPERTY].split(':')
			try:
				abspath = os.path.abspath(os.path.dirname(__file__))
				if abspath not in sys.path:
					sys.path.insert(0,abspath)
					
					module = __import__(str('.'.join(key[0:-1])), globals(), locals, str(key[-1])) #### FIX THIS
					imported_class = getattr(module, key[-1])
					obj = imported_class()
				
					_class_map[obj.class_key()] = obj.__class__
				
					return obj.from_entity(entity)

			except ImportError:
				raise db.KindError('Could not import model hierarchy \'%s\'' % str(key))
		
		
		if (_CLASS_KEY_PROPERTY in entity and
			tuple(entity[_CLASS_KEY_PROPERTY]) != cls.class_key()):
			key = tuple(entity[_CLASS_KEY_PROPERTY])
			try:
				poly_class = _class_map[key]
			except KeyError:
				raise db.KindError('No implementation for class \'%s\'' % (key,))
			
			return poly_class.from_entity(entity)
		return super(SPIPolyModel, cls).from_entity(entity)
		

	@classmethod
	def class_key_as_list(cls):

		""" Returns class path (in list form). """

		if not hasattr(cls, '__class_hierarchy__'):
			raise NotImplementedError('Cannot determine class key without class hierarchy')
		return list(cls.class_name() for cls in cls.__class_hierarchy__)
						

	@classmethod
	def all(cls, **kwds):
		query = super(PolyModel, cls).all(**kwds)
		if cls != PolyModel:
			query.filter(_CLASS_KEY_PROPERTY + ' =', cls.class_name())
		return query


	@classmethod
	def gql(cls, query_string, *args, **kwds):
		if cls == cls.__root_class__:
			return super(PolyModel, cls).gql(query_string, *args, **kwds)
		else:
			from google.appengine.ext import gql
			
			query = db.GqlQuery('SELECT * FROM %s %s' % (cls.kind(), query_string))

			query_filter = [('nop',[gql.Literal(cls.class_name())])]
			query._proto_query.filters()[(_CLASS_KEY_PROPERTY, '=')] = query_filter
			query.bind(*args, **kwds)
			return query