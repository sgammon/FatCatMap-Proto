from google.appengine.ext import db


class FCMModelMixin(object):
	
	''' Abstract parent for a data model mixin class. Designed to chunk down functionality to make it easier to mix and match different classes, without messing up MRO. '''
	
	__metaclass__ = db.PropertiedClass

	@classmethod
	def kind(self):
		"""Need to implement this because it is called by PropertiedClass
		to register the kind name in _kind_map. We just return a dummy name-
		a mixin does not store data in the datastore.
		"""
		
		return '__model_mixin__'