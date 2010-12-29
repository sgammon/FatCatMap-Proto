from google.appengine.ext import db
from google.appengine.api import channel
from google.appengine.api import taskqueue

from momentum.fatcatmap.workers import FCMWorker


class OpenSecretsManager(FCMWorker):

    def execute(self, **kwargs):
        pass


    @cached_property
    def serviceConfig(self):
        return config.config.get('services.opensecrets')