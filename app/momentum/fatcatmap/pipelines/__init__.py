import sys

if 'lib' not in sys.path:
    sys.path.insert(1, 'lib')

import config
import logging
import pipeline

from google.appengine.ext import db
from google.appengine.api import xmpp
from google.appengine.api import channel
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from momentum.fatcatmap.models.services import NodeID
from momentum.fatcatmap.models.services import ExtService
from momentum.fatcatmap.models.services import ExtServiceKey

from momentum.fatcatmap.core.data.json import FCMJSONAdapter


#### ==== Pipeline Support Framework ==== ####
class FCMPipelineLogger(object):

    enable = False
    dispatch_args = {}
    pipeline_obj = None

    def __init__(self, pipeline, **kwargs):
        self.pipeline_obj = pipeline
        self.dispatch_args = kwargs

    def debug(self, message):
        self._dispatch(self.pipeline_obj, 'debug', message, **self.dispatch_args)

    def info(self, message):
        self._dispatch(self.pipeline_obj, 'info', message, **self.dispatch_args)

    def warning(self, message):
        self._dispatch(self.pipeline_obj, 'warning', message, **self.dispatch_args)

    def error(self, message):
        self._dispatch(self.pipeline_obj, 'error', message, **self.dispatch_args)

    def exception(self, exception):
        self._dispatch(self.pipeline_obj, 'exception', str(exception), **self.dispatch_args)

    def critical(self, message):
        self._dispatch(self.pipline_obj, 'critical', str(message), **self.dispatch_args)

    def _dispatch(self, *args, **kwargs):
        if self.enable:
            self.dispatch(*args, **kwargs)
        else:
            pass

    def dispatch(self, *args, **kwargs):
        raise NotImplementedError('FCMPipelineLogger cannot be used directly to dispatch log messages.')



#### XMPP Logger
class FCMXMPPLogger(FCMPipelineLogger):


    def dispatch(self, pipeline, severity, message, jid=None):
        try:
            xmpp.send_message(jid, FCMJSONAdapter().encode({'_pc_message_type':'log_message', 'severity': severity, 'message': message}))
        except:
            pass
        

#### Channel Logger
class FCMChannelLogger(FCMPipelineLogger):

    def dispatch(self, pipeline, severity, message, channel_id=None):
        try:
            channel.send_message(channel_id, FCMJSONAdapter().encode({'_pc_message_type':'log_message','severity':severity, 'message':message}))
        except:
            pass


#### Serverlogs Logger
class FCMStandardLogger(FCMPipelineLogger):

    def debug(self, message): logging.info(message)
    def info(self, message): logging.info(message)
    def warning(self, message): logging.warning(message)
    def error(self, message): logging.error(message)
    def critical(self, message): logging.critical(message)


#### No Logging
class FCMDummyLogger(FCMPipelineLogger):

    def dispatch(self, *args, **kwargs):
        return None


#### Cache Adapter
class FCMPipelineCacheAdapter(object):

    @classmethod
    def set(cls, key, value, time=3600):
        memcache.set(key, value, time)

    @classmethod
    def get(cls, key):
        return memcache.get(key)


#### ============== Pipeline Framework ============== ####
class FCMPipeline(pipeline.Pipeline):

    db = db
    _opts = {}
    memcache = memcache
    pipeline = pipeline
    taskqueue = taskqueue
    logger = None
    cache = FCMPipelineCacheAdapter

    def __init__(self, *args, **kwargs):

        ## Add Pipeline Config
        self.pipeline_config = config.config.get('momentum.fatcatmap.pipelines')

        ## Process pipeline options
        if '_opts' in kwargs:
            self._opts = kwargs['_opts']
            if 'logging' in kwargs['_opts']:
                
                if 'enable' in kwargs['_opts']['logging']:

                    if kwargs['_opts']['logging']['enable'] == True:
                        if 'mode' in kwargs['_opts']['logging']:

                            if kwargs['_opts']['logging']['mode'] == 'xmpp':
                                if 'jid' in kwargs['_opts']['logging']:
                                    self.logger = FCMXMPPLogger(self, jid=kwargs['_opts']['logging']['jid'])

                            elif kwargs['_opts']['logging']['mode'] == 'channel':
                                if 'channel' in kwargs['_opts']['logging']:
                                    self.logger = FCMChannelLogger(self, channel_id=kwargs['_opts']['logging']['channel'])

                            elif kwargs['_opts']['logging']['mode'] == 'serverlogs':
                                self.logger = FCMStandardLogger(self)

                    else:
                        self.logger = FCMDummyLogger(self)

        ## Pull down service (if there is one)
        if hasattr(self, 'service'):

            manifest = db.Key.from_path(ExtService.kind(), getattr(self, 'service'))

            self.service = {'manifest':manifest}
            keys = ExtServiceKey.all().ancestor(self.service['manifest']).order('-last_used').fetch(1)
            self.service['keys'] = keys

        ## Run Pre-Execute Hook
        if hasattr(self, 'pre_execute'):
            self.pre_execute()

        ## If debugger is still none, it defaults to the dummy or standard if we're in debug mode...
        if self.logger == None:
            if self.pipeline_config['debug'] == True:
                self.logger = FCMStandardLogger(self)
            else:
                self.logger = FCMDummyLogger(self)

        ## Pass it up the line...
        super(FCMPipeline, self).__init__(*args, **kwargs)

    @property
    def log(self):
        return self.logger


class TestPipeline(FCMPipeline):

    def run(self):
        return db.Key.from_path('Test', 'test')