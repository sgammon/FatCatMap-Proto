from momentum.fatcatmap.core.data import FCMModelMixin


class FormGeneratorMixin(FCMModelMixin):

	@classmethod
	def _get_form_config(cls):

		'''

		Converts a _form_config property on a model to a config format compatible with WTForms.

		'Field' in this case is a string referencing a property on a Google App Engine model
		that will eventually be converted into a form control.

		-----------------------------------------		
		_form_config Structure:
		-----------------------------------------

			- form (dict):
				A dict of arguments to pass to the form constructor.

			- exclude (list):
				A list of fields to exclude from the form.

			- fields (list of string or (2 or 3 member) tuple values]):
				This prop is taken to mean a list of the *only* fields to be included in the form.

				- If a string value is encountered, it considers it a regular field name.

				- If a two-member tuple value is encountered:
					- The first value is considered the field name.
					- If the second member is a dict, it is considered field arguments.
					- If the second member is also a string, it is considered a python module path
					  for an external form (momentum.fatcatmap.forms is automatically prepended).

				- If a three-member tuple value is encountered:
					- The first value is considered the field name.
					- The second value is considered a python module path for an external form
					  (momentum.fatcatmap.forms is automatically prepended).
					- The third value must be a dict, and is considered field arguments.


			- script_snippet (string or tuple of 2 strings):
				If a string is found, the form library operates on the 'north' section of a form
				in a template. If a tuple of 2 strings is found, it extracts them as 'north' and
				'south'.

				Once 'north' or ('north', 'south') are extracted, 'snippets/forms/' is prepended
				to the first or both values and included with the form object.

				If the form render macro encounters a form with either the first or both params,
				it includes them above (north) or below (south) of the form tag in a <script>
				element.


		'''

		# Default to 'none' for each cfg value
		cmp_config = {'exclude':None, 'only':None, 'field_list':None, 'field_args':None, 'form_args':None, 'script_snippet': None}

		if hasattr(cls, '_form_config'):

			f_cfg = getattr(cls, '_form_config')

			# Grab form constructor args
			if 'form' in f_cfg:
				cmp_config['form_args'] = f_cfg['form']

			# Grab 'exclude'
			if 'exclude' in f_cfg and 'only' not in f_cfg and 'fields' not in f_cfg: cmp_config['exclude'] = f_cfg['exclude']

			# Grab script snippet
			if 'script_snippet' in f_cfg: north, south = f_cfg['script_snippet'] or f_cfg['script_snippet'], None

			# Grab fields
			if 'fields' in f_cfg:
				cmp_config['field_list'] = []
				for form_field in f_cfg['fields']:

					if isinstance(form_field, tuple):

						# If it's a two member tuple...
						if len(form_field) == 2:

							field_name, value2 = form_field

							# If value2 is a string, it's a reference to an external form...
							if isinstance(value2, basestring):
								form_field = (field_name, value2)

							# Else if value2 is a dict, it's args for the field
							elif isinstance(value2, dict):
								if not isinstance(cmp_config['field_args'], dict): cmp_config['field_args'] = {}
								cmp_config['field_args'][field_name] = value2
								form_field = field_name


						# If it's a three member tuple...	
						if len(form_field) == 3:
							field_name, ext_form, field_args = form_field
							if not isinstance(cmp_config['field_args'], dict): cmp_config['field_args'] = {}
							cmp_config['field_args'][field_name] = field_args
							form_field = (field_name, ext_form)


					cmp_config['field_list'].append(form_field)

		return cmp_config