from google.appengine.ext import db

from momentum.fatcatmap.models.geo import District
from momentum.fatcatmap.models.person import Person
from momentum.fatcatmap.models.politics import PoliticalParty
from momentum.fatcatmap.models.politics import LegislativeHouse


class Legislator(Person):

    house = db.ReferenceProperty(LegislativeHouse, collection_name='members')
    district = db.ReferenceProperty(District, collection_name='members')
    party = db.ReferenceProperty(PoliticalParty, collection_name='legislators')

    in_office = db.BooleanProperty()

    office_phone = db.PhoneNumberProperty()
    office_fax = db.PhoneNumberProperty()
    office_address = db.PostalAddressProperty()
    
    official_website = db.LinkProperty()
    official_webform = db.LinkProperty()
    official_email = db.StringProperty()