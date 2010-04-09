from google.appengine.ext import webapp
from google.appengine.api import memcache
import logging
import wsgiref.handlers

class ClearCache(webapp.RequestHandler):
    
    def get(self):
        
        s = memcache.get_stats()
        memcache.flush_all()
        self.response.out.write('<b>cache flushed. '+str(s['items'])+' deleted.</b>')

class CheckCache(webapp.RequestHandler):
    def get(self):
        
        s = memcache.get_stats()
        self.response.out.write('<b>cache items: '+str(s['items'])+'.</b>')
        
def main():
    wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/dev/clear_cache', ClearCache),
                                                              ('/dev/check_cache', CheckCache)]))

if __name__ == '__main__':
    main()