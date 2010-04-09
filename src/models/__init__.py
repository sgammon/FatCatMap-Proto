from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class Party(db.Model):
    name = db.StringProperty(indexed=True)
    abbreviation = db.StringProperty(indexed=True)

class Cycle(db.Model):
    year = db.StringProperty(indexed=True)
    integer = db.IntegerProperty(indexed=True)
    presidential_year = db.BooleanProperty(default=False)

class Candidate(db.Model):
    title = db.StringProperty()
    display_text = db.StringProperty(indexed=True)
    firstname = db.StringProperty(indexed=True)
    middlename = db.StringProperty(indexed=True)
    lastname = db.StringProperty(indexed=True)
    name_suffix = db.StringProperty(indexed=True)
    nickname = db.StringProperty()
    state = db.StringProperty(indexed=True)
    district = db.StringProperty(indexed=True)
    gender = db.StringProperty()
    webform = db.StringProperty()
    
    last_index = db.DateTimeProperty(default=None)
    modified = db.DateTimeProperty(auto_now=True)
    created = db.DateTimeProperty(auto_now_add=True)
    
class CandidateAttribute(db.Expando):
    candidate = db.ReferenceProperty(Candidate,collection_name="attributes")
    index = db.StringProperty(indexed=True)
    
class CandidateContact(polymodel.PolyModel):
    label = db.StringProperty(indexed=True)
    
class CandidatePhoneNumber(CandidateContact):
    value = db.PhoneNumberProperty()
    
class CandidateEmailAddress(CandidateContact):
    value = db.EmailProperty()
   
class CandidatePhysicalAddress(CandidateContact):
    value = db.PostalAddressProperty()   
   
class CandidateWebsite(CandidateContact):
    social = db.BooleanProperty()
    value = db.StringProperty() 
    
class Campaign(db.Model):
    candidate = db.ReferenceProperty(Candidate,collection_name="campaigns")
    cycle = db.ReferenceProperty(Cycle,collection_name="campaigns")
    party = db.ReferenceProperty(Party,collection_name="campaigns")

class Contributor(db.Model):
    orgname = db.StringProperty(indexed=True)
    display_text = db.StringProperty(indexed=True)
    
    last_index = db.DateTimeProperty(default=None)
    modified = db.DateTimeProperty(auto_now=True)
    created = db.DateTimeProperty(auto_now_add=True)
    
class ContributorAttribute(db.Expando):
    contributor = db.ReferenceProperty(Contributor,collection_name="attributes")
    a_key = db.StringProperty(indexed=True,name="key")
    
class ContributorContact(polymodel.PolyModel):
    label = db.StringProperty(indexed=True)
    
class ContributorPhoneNumber(ContributorContact):
    value = db.PhoneNumberProperty()
    
class ContributorEmailAddress(ContributorContact):
    value = db.EmailProperty()
   
class ContributorWebsite(ContributorContact):
    social = db.BooleanProperty()
    value = db.StringProperty() 

class Donation(db.Model):
    contributor = db.ReferenceProperty(Contributor,collection_name="donations")
    campaign = db.ReferenceProperty(Campaign,collection_name="donations")
    candidate = db.ReferenceProperty(Candidate,collection_name="donations")
    amount = db.IntegerProperty()
    
class OSum(db.Model): ## Connection summary, for speedups
    subject = db.StringProperty() ## key of the item, also stored as key name
    connections = db.ListProperty(db.Key)
    
class CSum(db.Model): ## Connection summary, for speedups
    nodes = db.ListProperty(db.Key) ## key of the item, also stored as key name
    total_amount = db.IntegerProperty(default=0)
    total_count = db.IntegerProperty(default=1)
        