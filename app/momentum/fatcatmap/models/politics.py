from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.geo import USState
from momentum.fatcatmap.models.geo import District

from momentum.fatcatmap.models.group import Group
from momentum.fatcatmap.models.group import Committee


#### ==== Legislature Models ==== ####
class Legislature(PolyPro):
    name = db.StringProperty()
    short_name = db.StringProperty()
    total_members = db.IntegerProperty()

class StateLegislature(Legislature):
    state = db.ReferenceProperty(USState, collection_name='legislature')


#### ==== Legislative House Models ==== ####
class LegislativeChamber(PolyPro):
    name = db.StringProperty()
    short_name = db.StringProperty()
    title_abbr = db.StringProperty()
    legislature = db.ReferenceProperty(Legislature, collection_name='houses')
    total_members = db.IntegerProperty()

class UpperLegislativeChamber(LegislativeChamber):
    pass

class LowerLegislativeChamber(LegislativeChamber):
    pass


#### ==== District/Seat Models ==== ####
class UpperChamberDistrict(District):
    seniority = db.StringProperty(choices=['junior','senior'])
    chamber = db.ReferenceProperty(UpperLegislativeChamber, collection_name='districts')

class LowerChamberDistrict(District):
    number = db.IntegerProperty()
    chamber = db.ReferenceProperty(LowerLegislativeChamber, collection_name='districts')


#### ==== Party Politics ==== ####
class PoliticalParty(Group):
    pass

class ElectionCycle(Model):
    presidential_election = db.BooleanProperty(default=False)


#### ==== Legislative Committees ==== ####
class LegislativeCommittee(Committee):
    name = db.StringProperty()
    code = db.StringProperty()
    legislature = db.ReferenceProperty()
    parent_committee = db.SelfReferenceProperty(collection_name='subcommittees')

    
class JointCommittee(LegislativeCommittee):
    chamber = db.ListProperty(db.Key)


class UpperChamberCommittee(LegislativeCommittee):
    chamber = db.ReferenceProperty(UpperLegislativeChamber, collection_name='committees')


class LowerChamberCommittee(LegislativeCommittee):
    chamber = db.ReferenceProperty(LowerLegislativeChamber, collection_name='committees')