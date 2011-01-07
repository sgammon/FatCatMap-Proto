# -*- coding: utf-8 -*-
"""
    config
    ~~~~~~

    Configuration settings.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE for more details.
"""
import os
import datetime

config = {}

## Check if we're running the app server
debug = os.environ.get('SERVER_SOFTWARE', '').startswith('Dev')

# ========= Tipfy Config ========= #

# Master Config
config['tipfy'] = {

    # Basic Config Values
    #'server_name': 'localhost:8080' if debug == True else 'fatcatmap.staging.ext.providenceclarity.com',

    # Installed middleware modules
    'middleware': [
    
        # Display Midleware
        #'tipfy.ext.i18n.I18nMiddleware',  ## Enables automatic string translations based on locale of user
    
        # Debugging Middleware
        'tipfy.ext.debugger.DebuggerMiddleware',  ## Enable debugger. It will be loaded only when executed from the dev environment.
        #'tipfy.ext.appstats.AppstatsMiddleware',  ## Enable for good code profiling information
        
        # FCM Stuff
        #'tipfy.ext.multitenancy.MultitenancyMiddleware',  ## Automatically extracts a namespace string from subdomains/URL parameters
        
    ],

    # Installed app packages
    'apps_installed': [
        'momentum.fatcatmap',  ## FatCatMap Package
    ],
    
}

# Session Config
config['tipfy.ext.session'] = {
    'secret_key': 'DShfodhob)*#G!@*G@)Gbv7f1cciocB*$BV&$@V#Cv86yvcb7376',  ## Salt for secure cookies
    'default_backend': 'datastore',  ## Can be used with datastore or memcache, too
	'cookie_name': 'momentum.fatcatmap.session'
}

# Jinja2 Config
config['tipfy.ext.jinja2'] = {
   # 'engine_factory': 'momentum.fatcatmap.core.output.fcmLoaderFactory'  ## Custom loader mapping with caching + stats + tracking features
}


# ========= Wirestone FCM Config ========= #

# Main Config
config['momentum.fatcatmap'] = {

    'version_major': 0,
    'version_minor': 7,
    'version_micro': 20101217,
	'version_phase': 'ALPHA'

}

# Env Configuration
config['momentum.fatcatmap.env'] = {

	'platform': {
	
		'dev': True if os.environ['SERVER_SOFTWARE'].startswith('Dev') else False
	
	}

}

# Dev Configuration
config['momentum.fatcatmap.dev'] = {

    'debug':True,  ## General debug features like Werkzeug and killswitch for param dumps
	'dev_mode':True, ## Appends version to title, enables values below
    'debug_markup': True, ## Enable output of HTML comments for easy debugging    
    'force_append_dev_footer': False,  ## Force appending a tiny dev footer with request and env stuff
    'request_logging': True,  ## Whether to enable general logging in request handlers

}

# Data/Modeling Configuration
config['momentum.fatcatmap.data'] = {

	'repo_by_reference': True, ## Sets a content item's repo by reference
	'repo_by_parent': False, ## Sets a content item's repo by parent-child
	'repo_by_namespace': False ## Sets a content item's repo by namespace

}

# API Configuration
config['momentum.fatcatmap.api'] = {

	'debug': False, ## Turns on debug logging for the API dispatcher and API requests

}

# Pipelines Configuration
config['momentum.fatcatmap.pipelines'] = {

    'debug': True

}

# Auth Configuration
config['momentum.fatcatmap.auth'] = {
	
	'debug': False,
	'ticket_lifetime': datetime.timedelta(hours=6),
	'enable_federated_logon': False
	
}

config['momentum.fatcatmap.auth.openid'] = {

	#'endpoint': 'http://webstaging.wirestone.com/AssetsAuth/openid-mvc/Default.aspx'
	'endpoint': 'https://www.google.com/accounts/o8/id'

}

# Security Configuration
config['momentum.fatcatmap.security'] = {

	'sysadmins_only': True,  ## Only allow in appengine-defined sysadmins ## DEPREACATED @TODO
    'check_repo_permissions': True  ## Whether to perform checks on use repo access permissions.

}

# Output Configuration
config['momentum.fatcatmap.output'] = {

    'enable_rest_api': False  ## Whether to enable the REST api for endpoints that lead to models

}

# Social Configuration
config['momentum.fatcatmap.social'] = {

	'enable_ajax_logging':False,

}

config['momentum.fatcatmap.output.request_handler'] = {

	'dependencies':
	{
		'packages':{
		
			'main': {'enabled':True,'module': 'momentum.fatcatmap.handlers.ext.main.Main'},
			'forms': {'enabled':True,'module': 'momentum.fatcatmap.handlers.ext.main.Forms'},			
			'jquery':{'enabled':True,'module':'momentum.fatcatmap.handlers.ext.jquery.jQuery'},
			'plupload':{'enabled':True,'module':'momentum.fatcatmap.handlers.ext.plupload.Plupload'},
			'datagrid':{'enabled':True,'module':'momentum.fatcatmap.handlers.ext.datagrid.DataGrid'},
			'protovis':{'enabled':True,'module':'momentum.fatcatmap.handlers.ext.protovis.Protovis'},			
			'autocomplete':{'enabled':True,'module':'momentum.fatcatmap.handlers.ext.autocomplete.AutoComplete'}
		
		},
		
		'always_include':['main','jquery','forms','datagrid']
	}

}

config['momentum.fatcatmap.output.template_loader'] = {

    'debug': False,  ## Enable dev logging
	'use_memory_cache': True, ## Use handler in-memory cache for template bytecode
	'use_memcache': True, ## Use Memcache API for template bytecode

}

# Configuration for polymodel
config['momentum.fatcatmap.datamodel.polymodel'] = {

	'class_property_name':'_class_',
	'path_property_name':'_path_'

}

# Configuration for system+user tickets
config['momentum.fatcatmap.datamodel.ticket'] = {

	'default_lifetime': datetime.timedelta(hours=8),
	
}

# Configuration for repository handling
config['momentum.fatcatmap.datamodel.repository'] = {

	'max_repositories':25

}

# Configuration for content item handling
config['momentum.fatcatmap.datamodel.content_item'] = {

	'extensions':
	{
		'_default_': 'file.html',
		'Document': 'document.html',
		'Image': 'image.html',
		'Video': 'video.html'
	}

}

# Ticket worker
config['momentum.fatcatmap.workers.ticketManager'] = {

	'debug': False

}

# Indexer
config['momentum.fatcatmap.workers.indexer'] = {
	
	'debug':True,
	'autoqueue':True

}

## Services Config
config['services.sunlight'] = {

    'api_key':'5716fd8eb1ce418095fe402c7489281e'

}

config['services.opensecrets'] = {



}