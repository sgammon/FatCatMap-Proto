### Basic Imports
import os
import config
import logging
import mimetypes
import simplejson as json

### App Engine Imports
from google.appengine.ext import db
from google.appengine.api import quota
from google.appengine.api import memcache
from google.appengine.ext import blobstore

### Tipfy Imports
from tipfy import abort
from tipfy import Tipfy
from tipfy import url_for
from tipfy import redirect
from tipfy import redirect_to
from tipfy import Response
from tipfy import RequestHandler
from tipfy import cached_property

### Tipfy Extensions: Authentication/Authorization
from tipfy.ext.auth import MultiAuthMixin
from tipfy.ext.auth import AppEngineAuthMixin
from tipfy.ext.auth import UserRequiredMiddleware
from tipfy.ext.auth import LoginRequiredMiddleware
from tipfy.ext.auth import AdminRequiredMiddleware

### Tipfy Extensions: Jinja2 Templating Engine
from tipfy.ext.jinja2 import Jinja2Mixin

### Tipfy Extensions: Session Handling
from tipfy.ext.session import FlashMixin
from tipfy.ext.session import CookieMixin
from tipfy.ext.session import SessionMixin
from tipfy.ext.session import MessagesMixin
from tipfy.ext.session import SessionMiddleware
from tipfy.ext.session import SecureCookieMixin

### Tipfy Extensions: Blobstore
from tipfy.ext.blobstore import BlobstoreUploadMixin
from tipfy.ext.blobstore import BlobstoreDownloadMixin


_dependency_cache = {}
_universal_middleware = [SessionMiddleware]


class BaseFCMRequestHandler(RequestHandler):
	pass
	
	
class FCMRequestHandler(BaseFCMRequestHandler, FlashMixin, SessionMixin, MessagesMixin, SecureCookieMixin, Jinja2Mixin):

	''' Parent class to all request handlers. '''

	## Set middleware and universal dependencies
	middleware = [SessionMiddleware]
	universal_dependencies = ['jQuery','main','social']

	## Map some useful variables
	config = config
	logging = logging
	app = Tipfy.app

	## Map some useful functions to methods
	def response(self, content='', headers={}):
		r = Response(content)
		for header_key, header_value in headers.items():
			r.headers[header_key] = header_value
		return r

	def redirect(self, address, empty_data=False, headers={}, cookies=[], **kwargs):
		r = redirect(address, **kwargs)

		if empty_data == True:
			r.data = ''

		for header_key, header_value in headers.items():
			r.headers[header_key] = header_value

		for cookie_name, cookie_value, cookie_path in cookies:
			r.set_cookie(cookie_name, cookie_value, cookie_path, None)

		return r

	def redirect_to(self, endpoint, empty_data=False, headers={}, cookies=[], **kwargs):
		r = redirect_to(endpoint, **kwargs)

		if empty_data == True:
			r.data = ''

		for header_key, header_value in headers.items():
			r.headers[header_key] = header_value


		## @TODO: Debug this later...
		#for cookie_name, cookie_value, cookie_path in cookies:
		#	r.set_cookie(cookie_name, cookie_value, cookie_path, None)

		return r

	def get_model_form(self, *args, **kwargs):
		return get_model_form(*args, **kwargs)

	def abort(self, *args, **kwargs):
		return abort(*args, **kwargs)

	def url_for(self, *args, **kwargs):
		return url_for(*args, **kwargs)

	## Resolve and extract HTML from dependencies
	def _resolve_and_run_dependency(self, name):

		''' Resolves, loads, and returns a dependency module. '''

		global _dependency_cache

		cfg = self.get_config('momentum.fatcatmap.output.request_handler', 'dependencies')

		if name in cfg['packages']:
			if name not in _dependency_cache:
				path = cfg['packages'][name]['module'].split('.')
				try:
					_m = __import__('.'.join(path[0:-1]), globals(), locals(), [path[-1]])
					package = getattr(_m, path[-1])
				except:
					return False
				_dependency_cache[name] = {'name':name,'module':cfg['packages'][name]['module'],'north':package.north(), 'south':package.south()}
			return _dependency_cache[name]
		else:
			return False

	## Load dependencies
	def load_dependencies(self, local):

		''' Parses dependencies list and compiles it into a system var that is passed to __north and __south. '''

		cfg = self.get_config('momentum.fatcatmap.output.request_handler','dependencies')

		cmp_html = {'north':'', 'south':''}
		cmp_dependencies = cfg['always_include']+local
		if isinstance(cmp_dependencies, list) and len(cmp_dependencies) > 0:

			## Compile dependencies list and filter out invalid entries
			for dependency in [self._resolve_and_run_dependency(str(x).lower()) or False for x in cmp_dependencies]:

				## Generate log warning for invalid dependency - silent fail (important!)
				if dependency is False:
					logging.warning('Template dependency failed to load. Check packages config and module path.')
					continue

				## Add compiled HTML for valid dependency
				else:
					cmp_html['north'] += "\n".join(dependency['north'])
					cmp_html['south'] += "\n".join(dependency['south'])

		## Return compiled dependency HTML for north and south
		return (cmp_html['north'], cmp_html['south'])


	def render(self, template, vars={}, dependencies=[], **kwargs):

		''' Wrapper to Jinja2 '''

		app = self.app
		h_cfg = app.get_config('momentum.fatcatmap.output.request_handler')

		# Resolve template dependencies and generate HTML for north and south
		ext_north, ext_south = self.load_dependencies(dependencies)

		# Generate 'sys' variable
		sys = {

			'session':self.session,
			'request':self.request,
			'env':os.environ,
			'request':self.request,
			'config':config.config,
		}


		# sys kwarg is discarded to prevent injection
		if 'sys' in kwargs:
			del kwargs['sys']

		# Generate 'tpl' variable
		tpl = {

			'dependencies': {

				'north':ext_north, ## Compiled HTML for dependencies using north
				'south':ext_south ## Compiled HTML for dependencies using south

			}

		}

		# tpl kwarg is discarded to prevent injection
		if 'tpl' in kwargs:
			del kwargs['tpl']

		# 'vars' entries override conflicts with kwargs...
		if isinstance(vars, list) and len(vars) > 0:
			for var in vars:
				kwargs[var] = vars[var]

		# Add sys context, return rendered Jinja2 template

		return self.render_response(template, sys=sys, tpl=tpl, **kwargs)	


class FCMAdminRequestHandler(FCMRequestHandler):

	middleware = _universal_middleware


class FCMSecurityRequestHandler(RequestHandler, SessionMixin, CookieMixin, SecureCookieMixin, Jinja2Mixin):
	pass


class FCMServeHandler(FCMRequestHandler, BlobstoreDownloadMixin):

	def get(self, blobkey, filename=None):

		try:
			blob_info = blobstore.BlobInfo.get(blobkey)

			if blob_info == False:
				abort(404)

			else:
				filetype, encoding = mimetypes.guess_type(blob_info.filename)
				return self.send_blob(blob_info, content_type=filetype)

		except Exception, e:
			try:
				asset = db.get(db.Key(blobkey))
				if asset.storage_mode == 'blobstore':
					filetype, encoding = mimetypes.guess_type(asset.blobstore_data.filename)
					return self.send_blob(asset.blobstore_data, content_type=filetype)
				else:
					r = self.response()
					r.headers['Content-Disposition'] = 'inline;'
					filetype, encoding = mimetypes.guess_type(asset.name)
					r.headers['Content-Type'] = filetype
					r.data = asset.datastore_data
					return r

			except db.Error:
				abort(404)


class FCMDownloadHandler(FCMRequestHandler, BlobstoreDownloadMixin):

	def get(self, blobkey, filename=None):

		try:
			blob_info = blobstore.BlobInfo.get(blobkey)

			if blob_info == False:
				abort(404)

			else:

				return self.send_blob(blob_info, content_type=mimetypes.guess_type(blob_info.filename), save_as=blob_info.filename)

		except Exception, e:
			abort(404)