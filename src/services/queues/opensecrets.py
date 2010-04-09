import logging, hashlib
import wsgiref.handlers
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.api import urlfetch, memcache
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import simplejson
from models import *

class OpenSecretsWorker(webapp.RequestHandler):
    def post(self): # should run at most 1/s
        
        c = Candidate.get(self.request.get('candidate_key'))
        logging.info('Processing OpenSecrets for candidate '+str(c.key())+'...')
        res = urlfetch.fetch(self.request.get('os_url'))
        
        if res.status_code == 200:
            contributors = simplejson.loads(res.content)
        else:
            logging.error('Could not retrieve OpenSecrets URL: "'+self.request.get('os_url')+'". Code: '+str(res.status_code)+'.')
            logging.error('Error content: '+str(res.content))
            self.response.set_status(500)
            self.response.out.write('OpenSecrets retrieve failure.')
            
        donations_to_put = []
        
        for contributor in contributors["response"]["contributors"]["contributor"]:
            
            contributor = contributor["@attributes"]
            contributor["cycle"] = contributors["response"]["contributors"]["@attributes"]["cycle"]
            contributor["origin"] = contributors["response"]["contributors"]["@attributes"]["origin"]
            
            ### Find the campaign and cycle
            cm = memcache.get('campaign_cache::'+str(c)+'::'+str(contributor['cycle']))
            if cm is None:
                cms = Campaign.all()
                cms.filter('candidate =',c)
                cms.filter('cycle =',Cycle.get_by_key_name(contributor["cycle"]))
            
            
                ### Create/fetch the campaign
                if cms.count() == 1:
                    logging.info('One campaign exists.')
                    cm = cms.get()
                elif cms.count() == 0:
                    logging.info('Creating campaign...')
                    cm = Campaign(c,candidate=c,cycle=Cycle.get_by_key_name(contributor["cycle"])).put()
                elif cms.count() > 1:
                    logging.error('Multiple campaigns error.')
                    self.response.out.write('Multiple campaigns error.')
                    exit()
                    
                memcache.set('campaign_cache::'+str(c)+'::'+str(contributor['cycle']),cm,time=7200)
                
            ### Create the contributor record
            cn_hash = hashlib.sha256()
            cn_hash.update(contributor['org_name'])
            
            cn = memcache.get('contributor_cache::'+str(cn_hash.hexdigest()))
            if cn is None:
                cns = Contributor.all()
                cns.filter('orgname =',contributor["org_name"])
            
                if cns.count() == 1:
                    logging.info('One contributor exists.')
                    cn = cns.get()
                elif cns.count() == 0:
                    logging.info('Creating contributor...')
                    cn = Contributor(orgname=contributor["org_name"],display_text=contributor["org_name"]).put()
                elif cns.count() > 1:
                    logging.error('Multiple contributors error.')
                    self.response.out.write('Multiple contributors error.')
                    exit()
                    
                memcache.set('contributor_cache::'+str(cn_hash.hexdigest()),cn,time=7200)
                
            logging.info('Creating donation record:')
            logging.info('---candidate: '+str(c))
            logging.info('---contributor: '+str(cn))
            logging.info('---campaign: '+str(cm))
            logging.info('---total: '+contributor["total"])    
                
            hash = hashlib.sha256()
            hash.update(str(c)+':'+str(cn)+':'+str(cm))
            
            ### Create the donation record
            d = Donation(cm,key_name=hash.hexdigest())
            d.contributor=cn
            d.campaign=cm
            d.candidate=c
            d.amount=int(contributor["total"])
            
            donations_to_put.append(d)
            
            self.response.set_status(200)
            self.response.out.write('Fetch successful.')
            
        db.put(donations_to_put)
        
        
        
def main():
    wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/_ah/queue/opensecrets', OpenSecretsWorker)]))

if __name__ == '__main__':
    main()