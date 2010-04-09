import logging, re
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template

class Crossdomain(webapp.RequestHandler):
    def get(self):

        crossdomain = """
<?xml version="1.0"?>
<cross-domain-policy>
    <allow-access-from domain="*.appspot.com"/>
    <allow-access-from domain="*.fatcatmap.appspot.com"/>
    <allow-access-from domain="*.fatcatmap.com"/>
    <allow-access-from domain="*.fatcatmap.org"/>    
</cross-domain-policy>
        """
        self.response.out.write(crossdomain)
        
class CrossdomainMaster(webapp.RequestHandler):
    def get(self):

        crossdomain = """
<?xml version="1.0"?>
<cross-domain-policy>
    <site-control permitted-cross-domain-policies="all"/>
    <allow-access-from domain="*.appspot.com"/>
    <allow-access-from domain="*.fatcatmap.appspot.com"/>
    <allow-access-from domain="*.fatcatmap.com"/>
    <allow-access-from domain="*.fatcatmap.org"/>
</cross-domain-policy>
        """
        self.response.out.write(crossdomain)        
        
application = webapp.WSGIApplication([('/crossdomain.xml',CrossdomainMaster),('/_rpc/crossdomain.xml',Crossdomain)],debug=True)
        
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()