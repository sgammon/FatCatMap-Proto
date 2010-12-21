"""
Core: Output

Responsible for the task of finding and compiling templates to be sent to the browser.
Two levels of caching are implemented here - in-memory handler caching and memcache.

According to settings in the config.py, this module will attempt to load compiled
template code from the handler first, memcache second, and at last resort will compile
the template and store it in the cache.
"""

import os
import base64
import pprint
import config
import logging
import timesince
import byteconvert

from google.appengine.ext import db
from google.appengine.api import memcache

from tipfy import abort
from tipfy import Tipfy
from tipfy import url_for
from tipfy import redirect

from tipfy.ext.jinja2 import render_response as jrender
from tipfy.ext.jinja2 import Environment as JEnvironment
from tipfy.ext.jinja2 import ModuleLoader as JModuleLoader
from tipfy.ext.jinja2 import FileSystemLoader as JFileSystemLoader

from momentum.fatcatmap.core.data.encode import FCMJSONEncoder

try:
	from tipfy.ext import i18n
except (ImportError, AttributeError), e:
	i18n = None

try:
	t_data
except NameError:
	t_data = {}

# Superfast In-Memory Cache
def get_tdata_from_fastcache(name, do_log):

	if name in t_data:
		if do_log: logging.debug('OUTPUT_LOADER: Found bytecode in fastcache memory under key \''+str(base64.b64encode(name))+'\'.')
		return t_data[name]
	else: return None
	

# Memcache API loader
def get_tdata_from_memcache(name, do_log):
	
	data = memcache.get('tdata-'+name)
	if data is not None:
		if do_log: logging.debug('OUTPUT_LOADER: Found bytecode in memcache under key \'tdata-'+str(name)+'\'.')
		return data
	else: return None
	

# Loader class
class FCMLoader(JFileSystemLoader):
	
	def load(self, environment, name, globals=None):
		
		if globals is None:
			globals = {}

		# Load config
		app = Tipfy.app
		dev = app.get_config('momentum.fatcatmap.dev')
		y_cfg = app.get_config('momentum.fatcatmap.output.template_loader')
		
		# Encode in Base64
		b64_name = base64.b64encode(name)

		# Debug logging
		if y_cfg.get('debug') == True: do_log = True
		else: do_log = False
		if do_log: logging.debug('OUTPUT_LOADER: FCM Template Loader received request for name \''+str(name)+'\'.')
		
		# Don't do caching if we're in dev mode
		if dev['dev_mode'] == False:

			# Try the in-memory supercache
			if y_cfg.get('use_memory_cache') == True: bytecode = get_tdata_from_fastcache(b64_name, do_log)
			else: bytecode = None
		
			if bytecode is None: # Not found in fastcache
		
				if do_log: logging.debug('OUTPUT_LOADER: Template not found in fastcache.')
			
				# Fallback to memcache
				if y_cfg.get('use_memcache') == True: bytecode = get_tdata_from_memcache(b64_name, do_log)

				# Fallback to regular loader, then cache
				if bytecode is None: # Not found in memcache
				
					if do_log: logging.debug('OUTPUT_LOADER: Template not found in memcache.')
				
					source, filename, uptodate = self.get_source(environment, name)
					template = file(filename).read().decode('ascii').decode('utf-8')
					bytecode = environment.compile(template, raw=True)
				
					if do_log: logging.debug('OUTPUT_LOADER: Loaded, decoded, and compiled template code manually.')
				
					if y_cfg.get('use_memcache') == False:
						memcache.set('tdata-'+b64_name, bytecode)
						if do_log: logging.debug('OUTPUT_LOADER: Stored in memcache with key \'tdata-'+b64_name+'\'.')
				
				bytecode = compile(bytecode, name, 'exec')
			
				if y_cfg.get('use_memory_cache') == False:
					t_data[b64_name] = bytecode
					if do_log: logging.debug('OUTPUT_LOADER: Stored in fastcache with key \''+b64_name+'\'.')
	
		else: ## In dev mode, compile everything every time
		
			source, filename, uptodate = self.get_source(environment, name)
			template = file(filename).read().decode('ascii').decode('utf-8')
			bytecode = compile(environment.compile(template, raw=True), name, 'exec')
			
		# Return compiled template code
		return environment.template_class.from_code(environment, bytecode, globals)
		

def abs_url_for(endpoint, *args, **kwargs):
	if 'HTTPS' in os.environ:
		if os.environ['HTTPS'] == 'off':
			scheme = 'http'
		else:
			scheme = 'https'
	else:
		scheme = 'http'
		
	return scheme+'://'+os.environ['HTTP_HOST']+url_for(endpoint, *args, **kwargs)


# Template Factory
def fcmLoaderFactory():
	"""Returns the Jinja2 environment.

	:return:
		A ``jinja2.Environment`` instance.
	"""
	app = Tipfy.app
	cfg = app.get_config('tipfy.ext.jinja2')
	templates_compiled_target = cfg.get('templates_compiled_target')
	use_compiled = not app.dev or cfg.get( 'force_use_compiled')

	if templates_compiled_target is not None and use_compiled:
		# Use precompiled templates loaded from a module or zip.
		loader = JModuleLoader(templates_compiled_target)
	else:
		# Parse templates for every new environment instances.
		loader = FCMLoader(cfg.get('templates_dir'))

	if i18n:
		extensions = ['jinja2.ext.i18n']
	else:
		extensions = []

	# Initialize the environment.
	env = JEnvironment(loader=loader, extensions=extensions)
	
	# Initialize API Variable
	api = {
		'memcache': memcache
	}

	# Add global functions
	util = {
		'request':Tipfy.request,
		'converters':{
			'timesince':timesince.timesince,
			'byteconvert':byteconvert.humanize_bytes,
			'json':FCMJSONEncoder()
		},
		'getattr':getattr,
		'setattr':setattr,
		'pprint':pprint.pprint,
		'api': api,
		'abort':abort,
		'redirect':redirect,
		'get_config':app.get_config,
		'len': len,
		'type': type,
		'types':{
			'str':str,
			'basestring':basestring,
			'object':object,
			'int':int,
			'long':long,
			'float':float,
			'list':list,
			'dict':dict,
			'tuple':tuple,
			'appengine':{
			
				'db':{
					'key':db.Key,
					'model':db.Model
				}
			
			}
		}
	}
	
	# Set global functions
	env.globals['util'] = util
	env.globals['link'] = url_for
	env.globals['abs_link'] = abs_url_for
	
	if i18n:
		# Install i18n.
		trans = i18n.get_translations
		env.install_gettext_callables(
			lambda s: trans().ugettext(s),
			lambda s, p, n: trans().ungettext(s, p, n),
			newstyle=True)
		env.globals.update({
			'format_date':	   i18n.format_date,
			'format_time':	   i18n.format_time,
			'format_datetime': i18n.format_datetime,
		})

	return env