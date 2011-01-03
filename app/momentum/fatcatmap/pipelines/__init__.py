import sys

if 'lib' not in sys.path:
    sys.path.insert(1, 'lib')

import logging
import pipeline

from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from momentum.fatcatmap.models.services import NodeID
from momentum.fatcatmap.models.services import ExtService
from momentum.fatcatmap.models.services import ExtServiceKey


class FCMPipeline(pipeline.Pipeline):

    db = db
    memcache = memcache
    pipeline = pipeline
    taskqueue = taskqueue

    def __init__(self, *args, **kwargs):

        ## Pull down service (if there is one)
        if hasattr(self, 'service'):

            manifest = db.Key.from_path(ExtService.kind(), getattr(self, 'service'))

            self.service = {'manifest':manifest}
            keys = ExtServiceKey.all().ancestor(self.service['manifest']).order('-last_used').fetch(1)
            self.service['keys'] = keys

        ## Run Pre-Execute Hook
        if hasattr(self, 'pre_execute'):
            self.pre_execute()

        ## Pass it up the line...
        super(FCMPipeline, self).__init__(*args, **kwargs)


class TestPipeline(FCMPipeline):

    def run(self):
        return db.Key.from_path('Test', 'test')