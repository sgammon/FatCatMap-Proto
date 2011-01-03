from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.geo import USState
from momentum.fatcatmap.models.geo import District


#### ==== Legislature Models ==== ####
class Legislature(PolyPro):
    name = db.StringProperty()
    short_name = db.StringProperty()
    total_members = db.IntegerProperty()

class StateLegislature(Legislature):
    state = db.ReferenceProperty(USState, collection_name='legislature')


#### ==== Legislative House Models ==== ####
class LegislativeHouse(PolyPro):
    name = db.StringProperty()
    short_name = db.StringProperty()
    title_abbr = db.StringProperty()
    legislature = db.ReferenceProperty(Legislature, collection_name='houses')
    total_members = db.IntegerProperty()

class UpperLegislativeHouse(LegislativeHouse):
    pass

class LowerLegislativeHouse(LegislativeHouse):
    pass


#### ==== District/Seat Models ==== ####
class UpperHouseDistrict(District):
    seniority = db.StringProperty(choices=['junior','senior'])
    house = db.ReferenceProperty(UpperLegislativeHouse, collection_name='districts')

class LowerHouseDistrict(District):
    number = db.IntegerProperty()
    house = db.ReferenceProperty(LowerLegislativeHouse, collection_name='districts')


#### ==== Party Politics ==== ####
class PoliticalParty(Model):
    name = db.StringProperty()
    plural = db.StringProperty()
    singular = db.StringProperty()

class ElectionCycle(Model):
    presidential_election = db.BooleanProperty(default=False)