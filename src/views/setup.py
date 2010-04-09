import logging, re
from google.appengine.api import urlfetch
from google.appengine.api import memcache
from google.appengine.ext import deferred
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api.labs import taskqueue
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext.webapp import template
from models import *
import simplejson

class SunlightSetup(webapp.RequestHandler):
    def get(self):
        
        logging.info('Beginning setup work...')
        
        ## Delete old stuff first ##
        schema = []
        schema.append(Candidate.all())
        schema.append(Cycle.all())
        schema.append(Party.all())
        schema.append(Contributor.all())
        schema.append(CandidateAttribute.all())
        schema.append(CandidateContact.all())
        schema.append(Campaign.all())
        schema.append(ContributorAttribute.all())
        schema.append(ContributorContact.all())
        schema.append(Donation.all())
        
        for model in schema:
            logging.info('Deleting models of type '+str(model)+'.')
            for instance in model:
                instance.delete()
        
        ## Create political parties ##
        logging.info('Creating political parties...')
        dems = Party(name="Democratic",abbreviation='D',key_name='D').put()
        reps = Party(name="Republican",abbreviation='R',key_name='R').put()
        ind = Party(name="Independent",abbreviation='I',key_name='I').put()
        
        ## Create election cycles ##
        logging.info('Creating election cycles...')
        cycle2008 = Cycle(year="2008",integer=2008,presidential_year=True,key_name='2008')
        cycle2008.put()
        cycle2010 = Cycle(year="2010",integer=2010,presidential_Year=False,key_name='2010')
        cycle2010.put()
        
        logging.info('Fetching sunlight URL...')
        sunlight = urlfetch.fetch("http://services.sunlightlabs.com/api/legislators.getList.json?apikey=fa4970be9eb4d8753209e1795b225b50")
        
        #sunlight = """
        #{"response": {"legislators": [{"legislator": {"district": "1", "title": "Rep", "eventful_id": "P0-001-000016130-0", "in_office": true, "state": "HI", "crp_id": "N00007665", "official_rss": "http://www.house.gov/apps/list/press/hi01_abercrombie/RSS.xml", "party": "D", "email": "Neil.Abercrombie@mail.house.gov", "votesmart_id": "26827", "website": "http://www.house.gov/abercrombie/", "fax": "202-225-4580", "govtrack_id": "400001", "firstname": "Neil", "middlename": "", "lastname": "Abercrombie", "congress_office": "1502 Longworth House Office Building", "phone": "202-225-2726", "webform": "http://www.house.gov/abercrombie/e_form.shtml", "youtube_url": "http://www.youtube.com/hawaiirep1", "nickname": "", "bioguide_id": "A000014", "fec_id": "H6HI01121", "gender": "M", "senate_class": "", "name_suffix": "", "twitter_id": "neilabercrombie", "birthdate": "1938-06-26", "congresspedia_url": "http://www.opencongress.org/wiki/Neil_Abercrombie"}}, {"legislator": {"district": "5", "title": "Rep", "eventful_id": "P0-001-000016131-9", "in_office": true, "state": "NY", "crp_id": "N00001143", "official_rss": "http://www.house.gov/apps/list/press/ny05_ackerman/RSS.xml", "party": "D", "email": "", "votesmart_id": "26970", "website": "http://ackerman.house.gov/index.html", "fax": "202-225-1589", "govtrack_id": "400003", "firstname": "Gary", "middlename": "L.", "lastname": "Ackerman", "congress_office": "2243 Rayburn House Office Building", "phone": "202-225-2601", "webform": "http://www.house.gov/writerep", "youtube_url": "http://www.youtube.com/RepAckerman", "nickname": "", "bioguide_id": "A000022", "fec_id": "H4NY07011", "gender": "M", "senate_class": "", "name_suffix": "", "twitter_id": "", "birthdate": "1942-11-19", "congresspedia_url": "http://www.opencongress.org/wiki/Gary_Ackerman"}}, {"legislator": {"district": "4", "title": "Rep", "eventful_id": "P0-001-000016132-8", "in_office": true, "state": "AL", "crp_id": "N00003028", "official_rss": "http://aderholt.house.gov/", "party": "R", "email": "", "votesmart_id": "441", "website": "http://aderholt.house.gov/index.html", "fax": "202-225-5587", "govtrack_id": "400004", "firstname": "Robert", "middlename": "B.", "lastname": "Aderholt", "congress_office": "1433 Longworth House Office Building", "phone": "202-225-4876", "webform": "http://aderholt.house.gov/?sectionid=195&sectiontree=195", "youtube_url": "http://www.youtube.com/RobertAderholt", "nickname": "", "bioguide_id": "A000055", "fec_id": "H6AL04098", "gender": "M", "senate_class": "", "name_suffix": "", "twitter_id": "Robert_Aderholt", "birthdate": "1965-07-22", "congresspedia_url": "http://www.opencongress.org/wiki/Robert_Aderholt"}}, {"legislator": {"district": "3", "title": "Rep", "eventful_id": "", "in_office": true, "state": "NJ", "crp_id": "N00000812", "official_rss": "", "party": "D", "email": "", "votesmart_id": "4171", "website": "http://adler.house.gov/", "fax": "202-225-0778", "govtrack_id": "412264", "firstname": "John", "middlename": "H.", "lastname": "Adler", "congress_office": "1223 Longworth House Office Building", "phone": "202-225-4765", "webform": "https://forms.house.gov/adler/contact-form.shtml", "youtube_url": "", "nickname": "", "bioguide_id": "A000364", "fec_id": "H8NJ03156", "gender": "M", "senate_class": "", "name_suffix": "", "twitter_id": "", "birthdate": "1959-08-23", "congresspedia_url": "http://www.opencongress.org/wiki/John_Adler"}}]}}
        #"""
        
        #sunlight = simplejson.loads(sunlight)
        
        if sunlight.status_code == 200:
            logging.info('Sunlight success. Parsing JSON...')
            sunlight = simplejson.loads(sunlight.content)
        else:
            logging.error('Sunlight error! Exiting.')
            self.response.out.write('sunlight error.')
            exit()
        
        logging.info('Beginning legislator processing (total: '+str(len(sunlight["response"]["legislators"]))+')...')    
        
        for legislator in sunlight["response"]["legislators"]:
            legislator = legislator["legislator"]
            t = taskqueue.Task(url='/_ah/queue/sunlight',params={'candidate_json':simplejson.dumps(legislator)})
            t.add(queue_name='sunlight')
            
        self.response.out.write('Done.')
            
    def post(self):
        self.response.out.write('Post received.')

class OpenSecretsSetup(webapp.RequestHandler):
    def get(self):
        
        logging.info('Beginning setup work for OpenSecrets...')
        keylimit = 200
        apikeys = ["f7f9fafb69541c9ee712da43416608af","9ba4173ecb56fd4c692bbd1911c68835","f24e8fb9ab0a0cc9e5a3bb469256312f","c6a5f0e9d3c8699d464b58dce92e33ae"]
            
        candidates_attrs = CandidateAttribute.all()
        candidates_attrs.filter('index =','crp_id')
        candidates_attrs.fetch(candidates_attrs.count())
        
        logging.info('Retrieving OpenSecrets data for a total of '+str(candidates_attrs.count())+' candidates.')
        
        index = 0
        
        for candidate_attr in candidates_attrs:
            index = index+1
            
            if index <= keylimit:
                apikey = apikeys[0]
            elif index <= keylimit*2:
                apikey = apikeys[1]
            elif index <= keylimit*3:
                apikey = apikeys[2]
            elif index <= keylimit*4:
                apikey = apikeys[3]
            else:
                apikey = ''
            
            crp_id = candidate_attr.value
            c = candidate_attr.parent()
            
            url = 'http://www.opensecrets.org/api/?&apikey='+str(apikey)+'&output=json&method=candContrib&cid='+str(crp_id)
            candidate_key = c.key()
            t = taskqueue.Task(url='/_ah/queue/opensecrets',params={'os_url':url,'candidate_key':candidate_key})
            t.add(queue_name='opensecrets')
        
        self.response.out.write('Done.')    
        
class DisplayTextSetup(webapp.RequestHandler):
    def get(self):
        cs = Candidate.all()
        cn = Contributor.all()
        
        cs = cs.fetch(cs.count())
        cn = cn.fetch(cn.count())
        
        for c in cs:
            c.display_text = c.title+". "+c.firstname+" "+c.lastname+" ("+c.state+"-"+c.district+")"
            c.put()
            
        for c in cn:
            c.display_text = c.orgname
            c.put()
            
        self.response.out.write('Done.')
            

application = webapp.WSGIApplication([('/setup/sunlight',SunlightSetup),('/setup/opensecrets',OpenSecretsSetup),('/setup/displaytext',DisplayTextSetup)],debug=True)
        
def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()