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

import logging
import random
import sys
import time

from google.appengine.api import memcache, datastore
from google.appengine.ext import db
from google.appengine.runtime import DeadlineExceededError
from lovely.gae.async import defer

_sorting = {'asc':  datastore.Query.ASCENDING,
            'desc': datastore.Query.DESCENDING}

_operator = {'asc':  '>', 'desc': '<'}

def create_markers(kind,
                   batchsize=100,
                   attribute='__key__',
                   order='asc',
                   filters=[],
                   callback=None):
    mc_key = ('create_markers:%s-%s' % (
        time.time(), random.randint(1, sys.maxint))).replace('.','-')
    defer(_compute_markers, [mc_key, kind, attribute, order, batchsize],
          dict(callback=callback, filters=filters), once_only=False)
    return mc_key

def _compute_markers(mc_key, kind, attribute, order, batchsize,
                     filters=[], callback=None):
    logging.info('BatchHandler.execute %s' % repr(locals()))
    q = datastore.Query(kind, keys_only=True)
    q.Order((attribute, _sorting[order]))
    for l, r in filters:
        q[l] = r
    # the intermediate result
    i_res = memcache.get(mc_key) or []
    try:
        while True:
            if i_res:
                q['%s %s' % (attribute, _operator[order])] = i_res[-1]
            if not q.Count(): # required due to bug in sdk (#2875)
                break
            res = q.Get(1, batchsize-1)
            if not res:
                # this is the end because we have less than
                # batchsize items left
                break
            # look if our attribute is __key__ so we have it already
            if attribute == '__key__':
                lastval = res[-1]
            else:
                e = db.get(res[-1])
                lastval = getattr(e, attribute)
            i_res.append(lastval)
        memcache.set(mc_key, i_res)
        # we are finished, so we call the callback with the name
        if callback:
            defer(callback, [mc_key], once_only=False)
    except DeadlineExceededError:
        # we did not make it, add ourself again
        memcache.set(mc_key, i_res)
        defer(_compute_markers, [mc_key, kind, attribute, order, batchsize],
              dict(callback=callback, filters=filters), once_only=False)

