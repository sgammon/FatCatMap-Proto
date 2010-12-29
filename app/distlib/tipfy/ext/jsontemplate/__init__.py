# -*- coding: utf-8 -*-
"""
    tipfy.ext.jsontemplate
    ~~~~~~~~~~~~~~~~~~~~~~

    Minimal but powerful templating language implemented in multiple languages

    :copyright: 2010 Jure Vrscaj.
    :license: Apache, see LICENSE.txt for more details.
"""

import logging
log = logging.getLogger("tipfy.ext.jsontemplate")

import os

from tipfy import Tipfy

import jsontemplate

default_config = {
    'templates_dir': 'templates/json',
}

_cache = {}

def _mtime(filename):
    cfg = Tipfy.app.get_config('tipfy.ext.jsontemplate')
    path = os.path.join(cfg["templates_dir"], filename)
    return os.path.getmtime(path)

def get_source(filename):
    """ Returns a raw template string.

    :param filename:
        The template filename relative to the templates directory.
    """

    cfg = Tipfy.app.get_config('tipfy.ext.jsontemplate')
    path = os.path.join(cfg["templates_dir"], filename)
    return open(path).read()

def get_template(filename, klass=jsontemplate.Template):
    """ Returns a template object.

    :param filename:
        The template filename relative to the templates directory.
    """
    t = _cache.get(filename)
    if t and t._uptodate():
        return t
    t = _cache[filename] = klass(get_source(filename))
    mtime = _mtime(filename)
    t._uptodate = lambda: _mtime(filename) == mtime
    return t
    
def render_template(filename, **context):
    """Renders a JSON template.

    :param filename:
        The template filename, related to the templates directory.
    :param context:
        Keyword arguments used as variables in the rendered template.
    :return:
        A rendered template.
    """
    
    t = get_template(filename)
    return t.expand(**context)
