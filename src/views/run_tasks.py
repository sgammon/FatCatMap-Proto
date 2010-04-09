from google.appengine.ext import db, webapp
from google.appengine.api.labs import taskqueue
from google.appengine.ext.webapp.util import run_wsgi_app
from models import *
import simplejson

class RunTasks(webapp.RequestHandler):

    def get(self):
        """
        KLUDGE!!
        Provides automatic task execution on dev sdk. 
    
        1. Setup this view func under the url /run_tasks.
        2. If you aren't using django, modify end. (HttpResponse and redirect)
        3. Run the following in a shell (you may need to change to the port number):
            while true; do \
            wget -qO - http://localhost:8085/run_tasks/ | wget --keep-session-cookies -i - --delete-after --wait=5; \
            sleep 60; \
            done
    
        Todo:
            - Add support for tasks that POST
            - Add support for rate (requests per second)
        """
        import os
        if os.environ['SERVER_SOFTWARE'].startswith('Development'):
            from datetime import datetime
            from google.appengine.api import apiproxy_stub_map
    
            stub = apiproxy_stub_map.apiproxy.GetStub('taskqueue')
            tasks = []
            #get all the tasks for all the queues
            for queue in stub.GetQueues():
                tasks.extend( stub.GetTasks(queue['name']) )
    
            #keep only tasks that need to be executed
            now = datetime.now()
            tasks = filter(lambda t: datetime.strptime(t['eta'],'%Y/%m/%d %H:%M:%S') < now, tasks)
    
            #Add admin urls to all urls
            base_url = 'http://%s:%s' % ( os.environ['SERVER_NAME'], os.environ['SERVER_PORT'] )
            login_url = base_url + '/_ah/login?email=test@example.com&admin=True&action=Login&continue='
            result = '\n'.join( [ login_url + t['url'] for t in tasks] )
    
            #remove tasks from ques
            for queue in stub.GetQueues():
                stub.FlushQueue(queue['name'])
    
            return self.response.out.write(result)
        return self.redirect('/')
                           
