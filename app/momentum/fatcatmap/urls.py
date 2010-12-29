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
        Rule('/', endpoint='sandbox-index', handler='momentum.fatcatmap.handlers.dev.SandboxIndex'),
        Rule('/sandbox/data.js', endpoint='sandbox-data', handler='momentum.fatcatmap.handlers.dev.SandboxGraphQuery'),
        Rule('/sandbox/manage_data', endpoint='sandbox-add-data', handler='momentum.fatcatmap.handlers.dev.SandboxAddData'),
    ]

    return rules
