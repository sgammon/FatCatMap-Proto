from google.appengine.ext import webapp
from google.appengine.api import memcache
from google.appengine.ext.webapp.util import run_wsgi_app
from models import *
from services.newdata import *

parentlist = {}

class RecursiveTest(webapp.RequestHandler):

    def get(self):

        depth = self.request.get('depth',default_value=settings.grapher_depth)
        climit = self.request.get('depth',default_value=settings.grapher_climit)

        c = Candidate.all()
        c = c.fetch(1)
        
        c = c[0]
        
        #memkey = 'map::key_'+str(c.key())+'::depth_'+str(depth)+'::climit_'+str(climit)
        
        #map = memcache.get(memkey)
        map = None
        if map is None:
            map = mapObject((c.key()),None,True,int(depth),9)
            #memcache.set(memkey,map,time=7200)
        
        self.print_recursive(None,map)
   
    def print_recursive(self,parent,node,depth=1,omit_list=[]):
           
        indent = '='
          
        for i in range(1, depth):
           indent = indent+'====' 
        
        self.response.out.write(indent+node['display_text']+"<br />")
        
        for connection in range(0,len(node['object']['connections'])):
            
            # if we're mapping root, we don't need to compare anything
            #self.response.out.write('<br />key: '+str(node['key'])+'<br />')
            #self.response.out.write('parent: '+str(parent)+'<br /><br />')
            self.print_recursive(parent,node['object']['connections'][connection],depth+1)

application = webapp.WSGIApplication([('/test/recursive',RecursiveTest)],debug=True)
        
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()   