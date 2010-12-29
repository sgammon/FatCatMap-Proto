# -*- coding: utf-8 -*-
"""
    urls
    ~~~~

    URL definitions.

    :copyright: 2009 by tipfy.org.
    :license: BSD, see LICENSE.txt for more details.
"""
from tipfy import Rule


def get_rules(app):
    """Returns a list of URL rules for the Hello, World! application.

    :param app:
        The WSGI application instance.
    :return:
        A list of class:`tipfy.Rule` instances.
    """

    rules = [

        ## Sandbox Rules
        Rule('/sandbox/home', endpoint='sandbox-index', handler='momentum.fatcatmap.handlers.dev.SandboxIndex'),
        Rule('/sandbox/manage/data', endpoint='sandbox-manage-data', handler='momentum.fatcatmap.handlers.dev.SandboxManageData'),
        Rule('/sandbox/manage/data/<string:procedure>', endpoint='sandbox-data-procedure', handler='momentum.fatcatmap.handlers.dev.SandboxProcedure'),
        Rule('/sandbox/_data', endpoint='sandbox-data-endpoint', handler='momentum.fatcatmap.handlers.dev.DataRPC'),

        ## Workers for Sunlight & OpenSecrets APIs
        Rule('/_pc/workers/sunlight/<string:procedure>', endpoint='workers-sunlight', handler='momentum.fatcatmap.workers.sunlight.SunlightManager'),
        Rule('/_pc/workers/opensecrets/<string:procedure>', endpoint='workers-opensecrets', handler='momentum.fatcatmap.workers.sunlight.OpenSecretsManager'),

        Rule('/sandbox/data.js', endpoint='sandbox-data', handler='momentum.fatcatmap.handlers.dev.SandboxGraphQuery'),
        Rule('/sandbox/manage_data', endpoint='sandbox-add-data', handler='momentum.fatcatmap.handlers.dev.SandboxAddData'),
    ]

    return rules
