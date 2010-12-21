import os
import logging

from google.appengine.ext import db

from momentum.fatcatmap.models.system import _SystemProperty_
from momentum.fatcatmap.dev.default_data import all_functions


class WirestoneDevMiddleware(object):

	def pre_dispatch(self, handler):
		if os.environ.get('SERVER_SOFTWARE', '').startswith('Dev') == True: ## Only run if we're on the dev server
			p = _SystemProperty_.get_by_key_name('dev.default_data')
			if p is None or p.value == False:

				logging.info('================== WIRESTONE DEV MIDDLEWARE ==================')
				logging.info('--Default data not added. Running.')

				status = []
				results = []

				for item in all_functions:

					logging.debug('------- Running insert function "'+str(item.__name__)+".")
					result = item()
					if result is not None:
						logging.debug('---------- Result is not None. No errors encountered.')
						if isinstance(result[0], db.Model):
							logging.debug('---------- Created '+str(len(result))+' keys of kind '+str(result[0].kind())+'.')
						else:
							logging.debug('---------- Created '+str(len(result))+' keys.')
						logging.debug('---------- Appending results. New results length: '+str(len(results))+'.')
						status.append((str(item.__name__), len(result)))
					else:
						status.append((str(item.__name__), 0))
						
				_SystemProperty_(key_name='dev.default_data', name='dev.default_data', value=True).put()