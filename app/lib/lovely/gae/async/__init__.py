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

import hashlib
import logging
from pickle import loads, dumps

from google.appengine.api import memcache, apiproxy_stub_map
from google.appengine.api.labs import taskqueue
from google.appengine.ext import webapp



def _job_key(handlerIdent):
    return 'defer:' + hashlib.sha1(handlerIdent).hexdigest()

def defer(handler, args=[], kwargs={}, queue_name='default',
          once_only=True, name=None):

    """defers execution of handler with given args and kwargs, all
    arguments needs to be pickleable"""

    payload = dumps((handler, args, kwargs, once_only))
    if once_only:
        mc_key = _job_key(payload)
        if memcache.get(mc_key):
            return
        memcache.set(mc_key, 1)
    task = taskqueue.Task(url='/lovely.gae/async.ExecuteHandler',
                          name=name,
                          payload=payload)
    return task.add(queue_name)

def get_tasks(queue_name='default'):
    tq_api = apiproxy_stub_map.apiproxy.GetStub('taskqueue')
    return tq_api.GetTasks(queue_name)



class ExecuteHandler(webapp.RequestHandler):

    def post(self):
        payload = self.request.body_file.read()
        handler, args, kwargs, once_only = loads(payload)
        if once_only:
            memcache.delete(_job_key(payload))
        logging.info('ExecuteHandler %r %r %r', handler, args, kwargs)
        res = handler(*args, **kwargs)
        logging.info('ExecuteHandler success %r', res)
        self.response.out.write('OK')

HANDLER_TUPLES = (
    ('/lovely.gae/async.ExecuteHandler', ExecuteHandler),
    )

