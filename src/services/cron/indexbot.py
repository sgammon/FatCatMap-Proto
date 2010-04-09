import logging
import wsgiref.handlers
from google.appengine.api import memcache
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from models import *

class IndexBot(webapp.RequestHandler):
    
    def get(self):
        pass
    
class CandidatesBot(webapp.RequestHandler):
    
    def get(self):
        
        candidates = Candidate.all()
        
        cursor = memcache.get('cachebot::candidates_cursor')
        if cursor is not None:
            candidates.with_cursor(cursor)
            
        records = candidates.fetch(50)
        
        if len(records) < 50: memcache.delete('cachebot::candidates_cursor')
        else: memcache.set('cachebot::candidates_cursor',candidates.cursor(),time=7200)
        
        for record in records:
            
            if record.last_index == None or record.modified > record.last_index:
                
                t = taskqueue.Task(params={'key':str(record.key())},url='/_ah/queue/indexer')
                t.add('indexer')
                
        
class ContributorsBot(webapp.RequestHandler):

    def get(self):
        
        contributors = Contributor.all()
        
        cursor = memcache.get('cachebot::contributors_cursor')
        if cursor is not None:
            contributors.with_cursor(cursor)
            
        records = contributors.fetch(500)
        
        if len(records) < 500: memcache.delete('cachebot::contributors_cursor')
        else: memcache.set('cachebot::contributors_cursor',contributors.cursor(),time=7200)
        
        for record in records:
    
            if record.last_index == None or record.modified > record.last_index:
                
                t = taskqueue.Task(params={'key':str(record.key())},url='/_ah/queue/indexer')
                t.add('indexer')
                logging.info('Added to indexer queue: '+str(record.key()))

def main():
    wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/_ah/cron/indexer/candidates', CandidatesBot),
                                                              ('/_ah/cron/indexer/contributors',ContributorsBot),
                                                              ('/_ah/cron/indexer/general', IndexBot)]))

if __name__ == '__main__':
    main()