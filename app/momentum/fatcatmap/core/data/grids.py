from tipfy import url_for
from momentum.fatcatmap.core.data import FCMModelMixin

from momentum.fatcatmap.core.grids import FCMDataGrid
from momentum.fatcatmap.core.grids import get_model_grid


class GridGeneratorMixin(FCMModelMixin):

	@classmethod
	def _get_grid_config(cls):

		'''

		Converts a _grid_config property on a model to a config object for generating model forms on the fly.

		'Field' in this case is a string referencing a property on a Google App Engine model
		that could eventually be converted into a grid column.

		-----------------------------------------		
		_grid_config Structure:
		-----------------------------------------

			- grid (dict):
				A dict of arguments to pass to the form constructor.

			- exclude (list):
				A list of fields to exclude from the form.

			- columns (list of string or (2 or 3 member tuples) tuple values):
				This prop is taken to mean a list of the *only* properties/columns to be included in the grid.

				- If a two-member tuple value is encountered:
					- The first value is considered the column label.
					- The second value is considered the property name.
					
				- If a three-member tuple is encountered:
					- The first value is considered the column label.
					- The second value is considered the property name.
					- The third value is considered arguments to pass to the script column entry in Datagrids.

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
		cmp_config = {'columns':None, 'column_args':None, 'grid_args':None, 'script_snippet': (None, None)}

		if hasattr(cls, '_grid_config'):

			g_cfg = getattr(cls, '_grid_config')

			# Grab grid constructor args
			if 'grid' in g_cfg:
				cmp_config['grid_args'] = g_cfg['grid']

			# Grab script snippet
			if 'script_snippet' in g_cfg:
				val = g_cfg['script_snippet']
				if isinstance(val, tuple):
					north, south = g_cfg['script_snippet']
					cmp_config['script_snippet'] = (north, south)
				else:
					north = g_cfg['script_snippet']
					cmp_config['script_snippet'] = (north, None)

			# Grab fields
			if 'columns' in g_cfg:
				cmp_config['columns'] = []
				for column in g_cfg['columns']:

					if isinstance(column, tuple):

						# If it's a two member tuple...
						if len(column) == 2:
							column_name, column_label = column
							column_args = None

						# If it's a three member tuple...
						if len(column) == 3:
							column_name, column_label, column_args = column

					cmp_config['columns'].append((column_name, column_label, column_args))

			return cmp_config

		else:
			return None
			
		
	@classmethod
	def generateGrid(cls, **kwargs):
		
		## Follow config or autogenerate one
		cfg = cls._get_grid_config()
		if cfg is not None:
			grid = FCMDataGrid(config=cfg, **kwargs)				
		else:
			grid = get_model_grid(cls)

		## Return Grid
		return grid