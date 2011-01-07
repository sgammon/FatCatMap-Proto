from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.graph import Node
from momentum.fatcatmap.models.graph import Native
from momentum.fatcatmap.models.graph import DirectedEdge
from momentum.fatcatmap.models.graph import UndirectedEdge


## A node that is contains to a collection of nodes
class Group(Model):
    name = db.StringProperty()
    plural = db.StringProperty()
    singular = db.StringProperty()

## Links a node to a group
class GroupMembership(DirectedEdge):
    group = db.ReferenceProperty(Group, collection_name='members')
    is_leadership = db.BooleanProperty()

## Links a node to another node because they are both in a group
class GroupRelationship(UndirectedEdge):
    group = db.ReferenceProperty()


#### ==== Generic Groups ==== ####
class Committee(Native):
    pass # Ancestor for a group of people that is (in some capacity) official

class Caucus(Group):
    pass # Ancestor for a group of people that is (less) official than a Committee

class Demographic(Group):
    pass # Ancestor for models based on race, age, political leaning, economic class, etc