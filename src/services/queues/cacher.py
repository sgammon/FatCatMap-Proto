import logging
import wsgiref.handlers
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from models import *

class CacheWorker(webapp.RequestHandler):
    
    def post(self):
        pass             

def main():
    wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/_ah/queue/cacher', CacheWorker)]))

if __name__ == '__main__':
    main()