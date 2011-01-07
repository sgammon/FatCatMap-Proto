# -*- coding: utf-8 -*-
"""
    urls
    ~~~~

    URL definitions.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE.txt for more details.
"""
from tipfy import Rule
from tipfy import HandlerPrefix


def get_rules(app):
    """Returns a list of URL rules for the Hello, World! application.

    :param app:
        The WSGI application instance.
    :return:
        A list of class:`tipfy.Rule` instances.
    """

    rules = [

        ## Sandbox Rules
        HandlerPrefix('momentum.fatcatmap.handlers.dev.', [

            Rule('/', endpoint='landing', handler='SandboxProcedure'),
            Rule('/sandbox/home', endpoint='sandbox-index', handler='SandboxIndex'),
            Rule('/sandbox/manage/data', endpoint='sandbox-manage-data', handler='SandboxManageData'),
            Rule('/sandbox/manage/data/<string:procedure>', endpoint='sandbox-data-procedure', handler='SandboxProcedure'),
            Rule('/sandbox/_data', endpoint='sandbox-data-endpoint', handler='DataRPC'),
            Rule('/sandbox/data.js', endpoint='sandbox-data', handler='SandboxGraphQuery'),
            Rule('/sandbox/manage_data', endpoint='sandbox-add-data', handler='SandboxAddData'),

        ]),


        ## FatCatMap API Engine (codenamed Cheshire)
        HandlerPrefix('momentum.fatcatmap.handlers.api.', [


            ## Top-Level API Dispatch
            HandlerPrefix('CheshireDispatch', [

                Rule('/_pc/api', endpoint='cheshire-root-dispatch'), ## Root dispatch for global-scope API information and operations
                Rule('/_pc/api/<string:module>', endpoint='cheshire-module-dispatch'), ## Module-scope API dispatch
                Rule('/_pc/api/<path:method_path>', endpoint='cheshire-method'), ## Universal method dispatch
                Rule('/_pc/api/<path:method_path>.<string:output>', endpoint='cheshire-method-with-output'), ## Universal method dispatch

            ]),

        ]),

        ## Workers
        HandlerPrefix('momentum.fatcatmap.handlers.workers.', [

            Rule('/_pc/workers/sunlight/<string:procedure>', endpoint='workers-sunlight', handler='sunlight.SunlightManager'),
            Rule('/_pc/workers/opensecrets/<string:procedure>', endpoint='workers-opensecrets', handler='sunlight.OpenSecretsManager'),

        ]),

    ]

    return rules
