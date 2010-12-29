import logging

from tipfy.ext.wtforms import Form
from tipfy.ext.wtforms import fields as f

from wtforms import widgets
from wtforms import validators

from wtforms.ext.appengine.fields import GeoPtPropertyField

from momentum.fatcatmap.core.forms.fields import FCMReferencePropertyField
from momentum.fatcatmap.core.forms.fields import FCMStringListPropertyField

def get_TextField(kwargs):
	"""
	Returns a ``TextField``, applying the ``db.StringProperty`` length limit
	of 500 bytes.
	"""
	kwargs['validators'].append(validators.length(max=500))
	return f.TextField(**kwargs)


def get_IntegerField(kwargs):
	"""
	Returns an ``IntegerField``, applying the ``db.IntegerProperty`` range
	limits.
	"""
	v = validators.NumberRange(min=-0x8000000000000000, max=0x7fffffffffffffff)
	kwargs['validators'].append(v)
	return f.IntegerField(**kwargs)


def convert_StringProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.StringProperty``."""
	if prop.multiline:
		kwargs['validators'].append(validators.length(max=500))
		return f.TextAreaField(**kwargs)
	else:
		return get_TextField(kwargs)


def convert_ByteStringProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.ByteStringProperty``."""
	return get_TextField(kwargs)


def convert_BooleanProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.BooleanProperty``."""
	return f.BooleanField(**kwargs)


def convert_IntegerProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.IntegerProperty``."""
	return get_IntegerField(kwargs)


def convert_FloatProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.FloatProperty``."""
	return f.FloatField(kwargs)


def convert_DateTimeProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.DateTimeProperty``."""
	if prop.auto_now or prop.auto_now_add:
		return None

	return f.DateTimeField(format='%Y-%m-%d %H-%M-%S', **kwargs)


def convert_DateProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.DateProperty``."""
	if prop.auto_now or prop.auto_now_add:
		return None

	return f.DateTimeField(format='%Y-%m-%d', **kwargs)


def convert_TimeProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.TimeProperty``."""
	if prop.auto_now or prop.auto_now_add:
		return None

	return f.DateTimeField(format='%H-%M-%S', **kwargs)


def convert_ListProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.ListProperty``."""
	return None


def convert_StringListProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.StringListProperty``."""
	return FCMStringListPropertyField(**kwargs)


def convert_ReferenceProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.ReferenceProperty``."""
	kwargs['reference_class'] = prop.reference_class
	return FCMReferencePropertyField(**kwargs)


def convert_SelfReferenceProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.SelfReferenceProperty``."""
	return None


def convert_UserProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.UserProperty``."""
	return None


def convert_BlobProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.BlobProperty``."""
	return f.FileField(**kwargs)


def convert_TextProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.TextProperty``."""
	return f.TextAreaField(**kwargs)


def convert_CategoryProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.CategoryProperty``."""
	return get_TextField(kwargs)


def convert_LinkProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.LinkProperty``."""
	kwargs['validators'].append(validators.url())
	return get_TextField(kwargs)


def convert_EmailProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.EmailProperty``."""
	kwargs['validators'].append(validators.email())
	return get_TextField(kwargs)


def convert_GeoPtProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.GeoPtProperty``."""
	return GeoPtPropertyField(**kwargs)


def convert_IMProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.IMProperty``."""
	return None


def convert_PhoneNumberProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.PhoneNumberProperty``."""
	return get_TextField(kwargs)


def convert_PostalAddressProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.PostalAddressProperty``."""
	return get_TextField(kwargs)


def convert_RatingProperty(model, prop, kwargs):
	"""Returns a form field for a ``db.RatingProperty``."""
	kwargs['validators'].append(validators.NumberRange(min=0, max=100))
	return f.IntegerField(**kwargs)


class FCMModelConverter(object):
	"""
	Converts properties from a ``db.Model`` class to form fields.

	Default conversions between properties and fields:

	+====================+===================+==============+==================+
	| Property subclass	 | Field subclass	 | datatype		| notes			   |
	+====================+===================+==============+==================+
	| StringProperty	 | TextField		 | unicode		| TextArea		   |
	|					 |					 |				| if multiline	   |
	+--------------------+-------------------+--------------+------------------+
	| ByteStringProperty | TextField		 | str			|				   |
	+--------------------+-------------------+--------------+------------------+
	| BooleanProperty	 | BooleanField		 | bool			|				   |
	+--------------------+-------------------+--------------+------------------+
	| IntegerProperty	 | IntegerField		 | int or long	|				   |
	+--------------------+-------------------+--------------+------------------+
	| FloatProperty		 | TextField		 | float		|				   |
	+--------------------+-------------------+--------------+------------------+
	| DateTimeProperty	 | DateTimeField	 | datetime		| skipped if	   |
	|					 |					 |				| auto_now[_add]   |
	+--------------------+-------------------+--------------+------------------+
	| DateProperty		 | DateTimeField	 | date			| skipped if	   |
	|					 |					 |				| auto_now[_add]   |
	+--------------------+-------------------+--------------+------------------+
	| TimeProperty		 | DateTimeField	 | time			| skipped if	   |
	|					 |					 |				| auto_now[_add]   |
	+--------------------+-------------------+--------------+------------------+
	| ListProperty		 | None				 | list			| always skipped   |
	+--------------------+-------------------+--------------+------------------+
	| StringListProperty | TextAreaField	 | list of str	|				   |
	+--------------------+-------------------+--------------+------------------+
	| ReferenceProperty	 | ReferencePropertyF| db.Model		|				   |
	+--------------------+-------------------+--------------+------------------+
	| SelfReferenceP.	 | ReferencePropertyF| db.Model		|				   |
	+--------------------+-------------------+--------------+------------------+
	| UserProperty		 | None				 | users.User	| always skipped   |
	+--------------------+-------------------+--------------+------------------+
	| BlobProperty		 | FileField		 | str			|				   |
	+--------------------+-------------------+--------------+------------------+
	| TextProperty		 | TextAreaField	 | unicode		|				   |
	+--------------------+-------------------+--------------+------------------+
	| CategoryProperty	 | TextField		 | unicode		|				   |
	+--------------------+-------------------+--------------+------------------+
	| LinkProperty		 | TextField		 | unicode		|				   |
	+--------------------+-------------------+--------------+------------------+
	| EmailProperty		 | TextField		 | unicode		|				   |
	+--------------------+-------------------+--------------+------------------+
	| GeoPtProperty		 | TextField		 | db.GeoPt		|				   |
	+--------------------+-------------------+--------------+------------------+
	| IMProperty		 | None				 | db.IM		| always skipped   |
	+--------------------+-------------------+--------------+------------------+
	| PhoneNumberProperty| TextField		 | unicode		|				   |
	+--------------------+-------------------+--------------+------------------+
	| PostalAddressP.	 | TextField		 | unicode		|				   |
	+--------------------+-------------------+--------------+------------------+
	| RatingProperty	 | IntegerField		 | int or long	|				   |
	+--------------------+-------------------+--------------+------------------+
	| _ReverseReferenceP.| None				 | <iterable>	| always skipped   |
	+====================+===================+==============+==================+
	"""

	default_converters = {
		'StringProperty':		 convert_StringProperty,
		'ByteStringProperty':	 convert_ByteStringProperty,
		'BooleanProperty':		 convert_BooleanProperty,
		'IntegerProperty':		 convert_IntegerProperty,
		'FloatProperty':		 convert_FloatProperty,
		'DateTimeProperty':		 convert_DateTimeProperty,
		'DateProperty':			 convert_DateProperty,
		'TimeProperty':			 convert_TimeProperty,
		'ListProperty':			 convert_ListProperty,
		'StringListProperty':	 convert_StringListProperty,
		'ReferenceProperty':	 convert_ReferenceProperty,
		'SelfReferenceProperty': convert_SelfReferenceProperty,
		'UserProperty':			 convert_UserProperty,
		'BlobProperty':			 convert_BlobProperty,
		'TextProperty':			 convert_TextProperty,
		'CategoryProperty':		 convert_CategoryProperty,
		'LinkProperty':			 convert_LinkProperty,
		'EmailProperty':		 convert_EmailProperty,
		'GeoPtProperty':		 convert_GeoPtProperty,
		'IMProperty':			 convert_IMProperty,
		'PhoneNumberProperty':	 convert_PhoneNumberProperty,
		'PostalAddressProperty': convert_PostalAddressProperty,
		'RatingProperty':		 convert_RatingProperty,
	}

	def __init__(self, converters=None):

		self.converters = converters or self.default_converters

	def convert(self, model, prop, field_args):

		kwargs = {
			'label': prop.name.replace('_', ' ').title(),
			'default': prop.default_value(),
			'validators': [],
		}
		if field_args:
			kwargs.update(field_args)

		if prop.required:
			kwargs['validators'].append(validators.required())

		if prop.choices:
			# Use choices in a select field.
			kwargs['choices'] = [(v, v) for v in prop.choices]
			return f.SelectField(**kwargs)
		else:
			converter = self.converters.get(type(prop).__name__, None)
			if converter is not None:
				return converter(model, prop, kwargs)
				

class FCMForm(Form):

	_action = None
	_method = 'post'
	_script_snippets = {'north':False, 'south':False}

	def set_action(self, action):
		self._action = action
		
	def set_method(self, method):
		self._method = method
		
	def set_script_snippets(self, value1, value2=None):

		if isinstance(value1, tuple):
			self._script_snippets['north'], self._script_snippets['south'] = value1
		else:
			self._script_snippets['north'] = value1
			if value2 is not None:
				self._script_snippets['south'] = value2
		
	def get_script_snippet(self, position):
		if position == 'north':
			if self._script_snippets['north'] != False:
				return 'snippets/forms/'+self._script_snippets['north']
		elif position == 'south':
			if self._script_snippets['north'] != False:			
				return 'snippets/forms/'+self._script_snippets['south']
		else: return None
		
	def get_action(self):
		return self._action
		
	def get_method(self):
		return self._method
		
		
def model_fields(model, only=None, exclude=None, field_args=None, converter=None):

	converter = converter or FCMModelConverter()
	field_args = field_args or {}

	# Get the field names we want to include or exclude, starting with the
	# full list of model properties.
	if hasattr(model, '_get_form_config'):

		f_cfg = model._get_form_config()

		props = model.properties()

		if 'field_list' in f_cfg:
			field_list = f_cfg['field_list']
		else:
			field_list = model.properties()

			if f_cfg['only']:
				field_list = [f for f in only if f in field_names]
			elif f_cfg['exclude']:
				field_names = [f for f in field_list if f not in exclude]

		# Grab model properties
		props = model.properties()

		# Create all fields.
		field_dict = {}
		for form_field in field_list:

			if isinstance(form_field, tuple):

				form_field_name, ext_form_path = form_field

				ext_form_class = getattr(__import__('.'.join(['wirestone','spi','forms']+ext_form_path.split('.')[0:-1]), globals(), locals(), [ext_form_path.split('.')[-1]]), ext_form_path.split('.')[-1])

				from momentum.fatcatmap.core.forms.fields import FCMExtFormField

				field_dict[form_field_name] = FCMExtFormField(ext_form_class, field_args.get(form_field))

			else:
				field = converter.convert(model, props[form_field], field_args.get(form_field))

				if field is not None:
					field_dict[form_field] = field

		return field_dict
	else:
		raise Exception("Failed to get form config for model kind '"+str(model.kind())+'". Make sure it implements FormGeneratorMixin.')		


def get_model_form(model, action=None, method='post', request=None, exclude_override=False, only_override=False, field_args_override=False, **kwargs):
	
	## Create form fields
	
	# Get form config
	f_cfg = model._get_form_config()
	
	# Generate form class
	f = type(model.kind() + 'Form', (FCMForm,), model_fields(model, exclude=exclude_override or f_cfg['exclude'], only=only_override or f_cfg['only'], field_args=field_args_override or f_cfg['field_args']))
	
	if request is not None and action is not None and method is not None:
		f = f(request, **kwargs)
	
		## Set action and method
		f.set_action(action)
		f.set_method(method)

	return f