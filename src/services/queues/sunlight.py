import logging
import wsgiref.handlers
from google.appengine.api.labs import taskqueue
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
import simplejson
from models import *

class SunlightWorker(webapp.RequestHandler):
    def post(self): # should run at most 1/s

        logging.info('Sunlight queue processing with JSON: '+self.request.get('candidate_json'))
        dems = Party.get_by_key_name('D')
        reps = Party.get_by_key_name('R')
        ind = Party.get_by_key_name('I')
        
        cycle2008 = Cycle.get_by_key_name('2008')
        cycle2010 = Cycle.get_by_key_name('2010')
        
        legislator = simplejson.loads(self.request.get('candidate_json'))
        
        def test():
            logging.info('Json received for task: '+str(self.request.get('candidate_json')))
        
        c = Candidate(key_name=legislator['crp_id'])
        displaytext = ''
        if legislator["firstname"] is not None and legislator["firstname"] is not '': c.firstname = legislator["firstname"]
        if legislator["middlename"] is not None and legislator["middlename"] is not '': c.middlename = legislator["middlename"]
        if legislator["lastname"] is not None and legislator["lastname"] is not '': c.lastname = legislator["lastname"]
        if legislator["name_suffix"] is not None and legislator["name_suffix"] is not '': c.name_suffix = legislator["name_suffix"]
        if legislator["nickname"] is not None and legislator["nickname"] is not '': c.nickname = legislator["nickname"]
        if legislator["state"] is not None and legislator["state"] is not '': c.state = legislator["state"]
        if legislator["district"] is not None and legislator["district"] is not '': c.district = legislator["district"]
        if legislator["gender"] is not None and legislator["gender"] is not '': c.gender = legislator["gender"]
        if legislator["webform"] is not None and legislator["webform"] is not '': c.webform = legislator["webform"]
        if legislator["title"] is not None and legislator["title"] is not '':
            c.title = legislator["title"]
            displaytext = displaytext+legislator["title"]+'. '
        if legislator["party"] is not None and legislator["party"] is not '':    
            if legislator["party"].lower() == 'd':
                c.party = dems
                c.partytext = 'D'
            elif legislator["party"].lower() == 'r':
                c.party = reps
                c.partytext = 'R'
            elif legislator["party"].lower() == 'i':
                c.party = ind
                c.partytext = 'I'
        
        if (legislator['district'] == 'Junior Seat') or (legislator['district'] == 'Senior Seat'): 
            displaytext = displaytext+legislator['firstname']+" "+legislator['lastname']+" ("+legislator['party']+'-'+legislator["state"]+")"
        else:
            displaytext = displaytext+legislator["firstname"]+" "+legislator["lastname"]+" ("+legislator['party']+'-'+legislator["state"]+legislator["district"]+")"
        c.display_text = displaytext
        
        c.put()
        
        def txn():
            
            try:
                if legislator["phone"] is not None and legislator["phone"] != '': CandidatePhoneNumber(c,label="Capital Phone",value=legislator["phone"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["fax"] is not None and legislator["fax"] != '': CandidatePhoneNumber(c,label="Capital Fax",value=legislator["fax"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["email"] is not None and legislator["email"] != '': CandidateEmailAddress(c,label="Capital Email",value=legislator["email"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["congress_office"] is not None and legislator["congress_office"] != '': CandidatePhysicalAddress(c,label="Capital Office",value=legislator["congress_office"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["website"] is not None and legislator["website"] != '': CandidateWebsite(c,label="Official",social=False,value=legislator["website"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["webform"] is not None and legislator["webform"] != '': CandidateWebsite(c,label="Webform",social=False,value=legislator["webform"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["congresspedia_url"] is not None and legislator["congresspedia_url"] != '': CandidateWebsite(c,label="Congresspedia",social=False,value=legislator["congresspedia_url"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["youtube_url"] is not None and legislator["youtube_url"] != '': CandidateWebsite(c,label="YouTube",social=True,value=legislator["youtube_url"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["twitter_id"] is not None and legislator["twitter_id"] != '': CandidateWebsite(c,label="Twitter",social=True,value="http://twitter.com/"+legislator["twitter_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["bioguide_id"] is not None and legislator["bioguide_id"] != '': CandidateAttribute(c,candidate=c,index="bioguide_id",value=legislator["bioguide_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["votesmart_id"] is not None and legislator["votesmart_id"] != '': CandidateAttribute(c,candidate=c,index="votesmart_id",value=legislator["votesmart_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["fec_id"] is not None and legislator["fec_id"] != '': CandidateAttribute(c,candidate=c,index="fec_id",value=legislator["fec_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["govtrack_id"] is not None and legislator["govtrack_id"] != '': CandidateAttribute(c,candidate=c,index="govtrack_id",value=legislator["govtrack_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["crp_id"] is not None and legislator["crp_id"] != '': CandidateAttribute(c,candidate=c,index="crp_id",value=legislator["crp_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["eventful_id"] is not None and legislator["eventful_id"] != '': CandidateAttribute(c,candidate=c,index="eventful_id",value=legislator["eventful_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["sunlight_old_id"] is not None and legislator["sunlight_old_id"] != '': CandidateAttribute(c,candidate=c,index="sunlight_old_id",value=legislator["sunlight_old_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if legislator["twitter_id"] is not None and legislator["twitter_id"] != '': CandidateAttribute(c,candidate=c,index="twitter_id",value=legislator["twitter_id"]).put()
            except KeyError, BadValueError: pass
            try:
                if str(legislator["in_office"]) is not None and str(legislator["in_office"]) != '':
                    if str(legislator["in_office"])=='1':
                        CandidateAttribute(c,candidate=c,index="in_office",value=True).put()
                    else:
                        CandidateAttribute(c,candidate=c,index="in_office",value=False).put()
            except KeyError, BadValueError: pass

        db.run_in_transaction(txn)
            
    def get(self):
        self.response.out.write('Must post to submit a task.')

def main():
    wsgiref.handlers.CGIHandler().run(webapp.WSGIApplication([('/_ah/queue/sunlight', SunlightWorker)]))

if __name__ == '__main__':
    main()