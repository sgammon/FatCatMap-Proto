from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
            
class LoginHandler(webapp.RequestHandler):
    def get(self):
        from google.appengine.api import users
        self.redirect(users.create_login_url('/'),True)
            
class LogoutHandler(webapp.RequestHandler):
    def get(self):
        from google.appengine.api import users
        self.redirect(users.create_logout_url('/'),True)            

application = webapp.WSGIApplication([('/login',LoginHandler),('/logout',LogoutHandler)],debug=True)
        
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()