from wtforms import fields as f
from wtforms import widgets as w

from momentum.fatcatmap.core.forms.widgets import BoxWidget


_unset_value = None

class SPIExtFormField(f.Field):
    """
    Encapsulate a form as a field in another form.

    :param form_class:
        A subclass of Form that will be encapsulated.
    :param separator:
        A string which will be suffixed to this field's name to create the
        prefix to enclosed fields. The default is fine for most uses.
    """
    widget = BoxWidget()

    def __init__(self, form_class, label=u'', validators=None, separator='-', **kwargs):
        super(SPIExtFormField, self).__init__(label, validators, **kwargs)
        self.form_class = form_class
        self.separator = separator
        self._obj = None
        if self.filters:
            raise TypeError('ExtFormField cannot take filters, as the encapsulated data is not mutable.')
        if validators:
            raise TypeError('ExtFormField does not accept any validators. Instead, define them on the enclosed form.')

    def process(self, formdata, data=_unset_value):
        if data is _unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default
            self._obj = data

        prefix = self.name + self.separator
        if isinstance(data, dict):
            self.form = self.form_class(formdata=formdata, prefix=prefix, **data)
        else:
            self.form = self.form_class(formdata=formdata, obj=data, prefix=prefix)

    def validate(self, form, extra_validators=tuple()):
        if extra_validators:
            raise TypeError('ExtFormField does not accept in-line validators, as it gets errors from the enclosed form.')
        return self.form.validate()

    def populate_obj(self, obj, name):
        candidate = getattr(obj, name, None)
        if candidate is None:
            if self._obj is None:
                raise TypeError('populate_obj: cannot find a value to populate from the provided obj or input data/defaults')
            candidate = self._obj
            setattr(obj, name, candidate)

        self.form.populate_obj(candidate)

    def __iter__(self):
        return iter(self.form)

    def __getitem__(self, name):
        return self.form[name]

    def __getattr__(self, name):
        return getattr(self.form, name)

    @property
    def data(self):
        return self.form.data

    @property
    def errors(self):
        return self.form.errors


class SPIReferencePropertyField(f.SelectFieldBase):
	"""
	A field for ``db.ReferenceProperty``. The list items are rendered in a
	select.
	
	Modded from the original to support a 'choices' override parameter.
	"""
	widget = w.Select()

	def __init__(self, label=u'', validators=None, reference_class=None,
				label_attr=None, choices=False, select_instruction_text=None, fetch_limit=50, allow_blank=False, blank_text=u'', **kwargs):
		super(SPIReferencePropertyField, self).__init__(label, validators,
													**kwargs)
		self.label_attr = label_attr
		self.allow_blank = allow_blank
		self.blank_text = blank_text
		self.choices = choices
		self.reference_class = reference_class
		self.select_instruction_text = select_instruction_text		
		self._set_data(None)
		if reference_class is None:
			raise TypeError('Missing reference_class attribute in '
							'ReferencePropertyField')

		self.query = reference_class.all().fetch(fetch_limit)

	def _get_data(self):
		if self._formdata is not None:
			for obj in self.query:
				key = str(obj.key())
				if key == self._formdata:
					self._set_data(key)
					break
		return self._data

	def _set_data(self, data):
		self._data = data
		self._formdata = None

	data = property(_get_data, _set_data)

	def iter_choices(self):

		if self.select_instruction_text is not None:
			yield (u'__None', '--- '+self.select_instruction_text+' ---', self.data is None)
		
		if self.allow_blank:
			yield (u'__None', self.blank_text, self.data is None)

		if self.choices != False:
			for label, value in self.choices:
				yield (value, label, value == self.data)
		else:
			for obj in self.query:
				key = str(obj.key())
				label = self.label_attr and getattr(obj, self.label_attr) or key
				yield (key, label, key == self.data)

	def process_formdata(self, valuelist):
		if valuelist:
			if valuelist[0] == '__None':
				self.data = None
			else:
				self._data = None
				self._formdata = valuelist[0]

	def pre_validate(self, form):
		if not self.allow_blank or self.data is not None:
			for obj in self.query:
				if self.data == str(obj.key()):
					break
				else:
					raise ValueError(self.gettext(u'Not a valid choice'))


class SPIStringListPropertyField(f.TextAreaField):
	"""
	A field for ``db.StringListProperty``. The list items are rendered in a
	textarea.
	"""
	def process_data(self, value):
		if isinstance(value, list):
			value = '\n'.join(value)

		self.data = value

	def populate_obj(self, obj, name):
		if isinstance(self.data, basestring):
			value = self.data.splitlines()
		else:
			value = []

		setattr(obj, name, value)
