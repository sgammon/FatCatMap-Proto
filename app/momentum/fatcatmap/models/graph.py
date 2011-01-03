from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro


#### ==== Graph-wide Models ==== ####
class Graph(Model):
	name = db.StringProperty()


#### ==== Models for Graph Nodes ==== ####
class NodeType(Model):
    name = db.StringProperty()
    description = db.TextProperty()
    native_impl_class = db.StringListProperty(indexed=False)

class Node(Model):
    label = db.StringProperty()
    type = db.ReferenceProperty(NodeType, collection_name='nodes')

class Native(PolyPro):
    version = db.IntegerProperty(default=1)
    node = db.ReferenceProperty(Node, collection_name='native')


#### ==== Models for Node Relationships ==== ####
class EdgeType(Model):
    name = db.StringProperty()
    description = db.TextProperty()

class Connection(Model):
    nodes = db.ListProperty(db.Key)
    score = db.FloatProperty(default=0.0)
    
class Edge(PolyPro):
    score = db.FloatProperty(default=0.0)
    target = db.ReferenceProperty(Node, collection_name='reverse_edges')
    partner = db.SelfReferenceProperty()
    partner_key = db.StringProperty()
    connection = db.ReferenceProperty(Connection, collection_name='edges')

class UndirectedEdge(PolyPro):
    pass

class DirectedEdge(PolyPro):
    is_source = db.BooleanProperty()