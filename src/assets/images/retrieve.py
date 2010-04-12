from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app

class DynamicImageHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('Not yet implemented.')
            
application = webapp.WSGIApplication([('/assets/images/.*',DynamicImageHandler)],debug=True)
        
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()