import config
import logging
import simplejson

from sunlightapi import sunlight

from tipfy import abort
from tipfy import cached_property

from google.appengine.ext import db
from google.appengine.api import channel
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from momentum.fatcatmap.workers import FCMWorker
from momentum.fatcatmap.handlers import FCMRequestHandler

from momentum.fatcatmap.models.system import TemporaryText

from momentum.fatcatmap.models.person import Person
from momentum.fatcatmap.models.sunlight import Legislator



sunlight_client = None


class SunlightWorker(FCMWorker):

    @cached_property
    def sunlight(self):
        global sunlight_client
        if sunlight_client is None:
            sunlight_client = sunlight
            sunlight_client.apikey = self.serviceConfig['api_key']
            return sunlight_client
        else:
            return sunlight_client

    @cached_property
    def serviceConfig(self):
        return config.config.get('services.sunlight')


class SunlightManager(SunlightWorker):

    def post(self, **kwargs):
        return self.get()

    def get(self, **kwargs):

        logging.info('Sunlight manager received request. Printing kwargs. ')
        logging.info('--Printing kwargs: '+str(kwargs))
        logging.info('--Printing params: '+str(self.params))

        ## Set up channel for progress information
        if 'channel' in self.params:
            channel.send_message(self.params['channel'], 'SunlightManager received task. Beginning execution.')
        else:
            return self.response('<b>No channel to update</b>')

        ## Get list
        legislators = self.sunlight.legislators.getList(state='CA')

        for legislator in legislators:

            channel.send_message(self.params['channel'], 'Received legislator "'+str(legislator)+'".')

        #logging.info('WORKING')
        return self.response('<b>Good</b>')