##############################################################################
#
# Copyright 2009 Lovely Systems AG
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
##############################################################################

import base64
import doctest
import unittest
from StringIO import StringIO

from google.appengine.api import apiproxy_stub_map
from google.appengine.ext import webapp
from lovely.gae.testing import DBLayer
from zope.testing.doctestunit import DocFileSuite


dbLayer = DBLayer('DBLayer')


def run_tasks(num=1000, queue_name='default', recursive=False):
    from lovely.gae.async import get_tasks, ExecuteHandler
    res = 0
    while True:
        tasks = get_tasks(queue_name)[:num]
        if not tasks:
            return res
        for task in tasks:
            if task['url'] != '/lovely.gae/async.ExecuteHandler':
                return
            body = base64.standard_b64decode(task['body'])
            headers = dict(task['headers'])
            headers['Content-Length'] = len(body)
            req = webapp.Request({
                'wsgi.input': StringIO(body),
                })
            req.headers = headers
            resp = webapp.Response()
            w = ExecuteHandler()
            w.initialize(req, resp)
            w.post()
            if w.response._Response__status[0] == 200:
                tq_api = apiproxy_stub_map.apiproxy.GetStub('taskqueue')
                tq_api.DeleteTask(queue_name, task['name'])
            res +=1
        if not recursive:
            return res

def setUp(test):
    tq_api = apiproxy_stub_map.apiproxy.GetStub('taskqueue')
    tq_api.FlushQueue('default')
    test.globs['run_tasks'] = run_tasks

def test_suite():
    readme = DocFileSuite('README.txt', setUp=setUp,
                           optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS,
                           )
    s = unittest.TestSuite((readme,))
    s.layer = dbLayer
    return s
