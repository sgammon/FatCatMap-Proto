import logging, datetime
import wsgiref.handlers
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from models import *

class IndexWorker(webapp.RequestHandler):
    
    def post(self):
        
        key = self.request.get('key',default_value=False)
        
        if key is False:
            self.set_status(200)
            self.response.out.write('No-key, pass.')
        
        else:
            obj = db.get(key)
            
            compiled_connections = {'keys':[],'index':{}}
            
            donations = Donation.all().filter(str(obj.kind()).lower()+' =',obj)
                
            count = donations.count()
            records = donations.fetch(count)
            
            if count > 0:
                
                for record in records:
                    if str(obj.kind()) == 'Candidate': fk = record.contributor
                    elif str(obj.kind()) == 'Contributor': fk = record.candidate
                
                    try:
                        compiled_connections['index'][str(fk)]
                    except:
                        compiled_connections['keys'].append(fk.key())
                        compiled_connections['index'][str(fk.key())] = {'amount':0,'count':0}
                    
                    compiled_connections['index'][str(fk.key())]['amount'] = compiled_connections['index'][str(fk.key())]['amount']+record.amount
                    compiled_connections['index'][str(fk.key())]['count'] = compiled_connections['index'][str(fk.key())]['count']+1
            
            if len(compiled_connections['keys']) > 0:
                
                cached = OSum.get_by_key_name(str(obj.key()))
                if cached is not None:
                    cached.delete()
                
                OSum(obj,
                     key_name=str(obj.key()),
                     subject=str(obj.key()),
                     connections=compiled_connections['keys']).put()
                
                csum_list = []
                
                for item in compiled_connections['keys']:
                    csum_list.append(CSum(nodes=[obj.key(),item],total_amount=compiled_connections['index'][str(item)]['amount']
                                               ,total_count=compiled_connections['index'][str(item)]['count']))
                    
                db.put(csum_list)
                
                     
            obj.last_index = datetime.datetime.now()
                     
            self.response.set_status(200)
            self.response.out.write('Success')

def main():
    wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/_ah/queue/indexer', IndexWorker)]))

if __name__ == '__main__':
    main()