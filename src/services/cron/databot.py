import logging
import wsgiref.handlers
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from models import *

class CacheBot(webapp.RequestHandler):
    
    def get(self):
        pass

def main():
    wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/_ah/cron/databot', DataBot)]))

if __name__ == '__main__':
    main()