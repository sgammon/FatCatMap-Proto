import config
import logging
import simplejson

from sunlightapi import sunlight

from tipfy import abort
from tipfy import cached_property

from google.appengine.ext import db
from google.appengine.api import channel
from google.appengine.api import taskqueue

from momentum.fatcatmap.workers import FCMWorker


sunlight_client = None


class SunlightWorker(FCMWorker):

    @cached_property
    def sunlight(self):
        global sunlight_client
        if sunlight_client is None:
            sunlight_client = sunlight
            sunlight_client.apikey = self.serviceConfig['api_key']
        else:
            return sunlight_client

    @cached_property
    def serviceConfig(self):
        return config.config.get('services.sunlight')


class SunlightManager(SunlightWorker):

    def execute(self, **kwargs):

        ## Set up channel for progress information
        if 'channel' in self.params:
            channel.send_message(self.params['channel'], 'SunlightManager received task. Beginning execution.')
        else:
            return self.response('<b>No channel to update</b>')

        ## Get list
        legislators = self.sunlight.legislators.getList(state='CA')

        for legislator in legislators:
            channel.send_message(self.params['channel'], 'Received legislator "'+str(legislator)+'".')

        logging.info('WORKING')
        return self.response('<b>Good</b>')