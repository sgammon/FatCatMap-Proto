import logging
from google.appengine.ext import db


class KeyProperty(db.StringProperty):
	
	_autofetch = False
	data_type = db.Key
	
	def __init__(self, autofetch=False):
		self._autofetch = autofetch
		super(KeyProperty, self).__init__()
				
	def validate(self, value):
		if isinstance(value, db.Key):
			return value
		elif isinstance(value, db.Model):
			return value.key()
		elif isinstance(value, basestring):
			value = db.Key(value)
			
		return value
			
	def make_value_from_datastore(self, value):
		if self._autofetch == True:
			return db.get(value)
		else:
			return value