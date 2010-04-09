from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from google.appengine.api import memcache, users

class FatCatMapHandler(webapp.RequestHandler):
    def get(self):
        
        if users.get_current_user() is not None:
            usertext = users.get_current_user().email()
            if users.is_current_user_admin():
                usertext + ' (ADMIN)'
        else:
            usertext = '(Not logged in)'
        
        self.response.out.write(template.render('../templates/fatcatmap.html', {'flash':'/assets/flash/main.swf','usertext':usertext}))

application = webapp.WSGIApplication([('/',FatCatMapHandler)],debug=True)
        
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()