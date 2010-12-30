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

class Node(Model):
    label = db.StringProperty()
    type = db.ReferenceProperty(NodeType, collection_name='nodes')

class Native(PolyPro):
    node = db.ReferenceProperty(Node, collection_name='native')
    version = db.IntegerProperty()


#### ==== Models for Node Relationships ==== ####
class EdgeType(Model):
    name = db.StringProperty()
    description = db.TextProperty()

class Edge(PolyPro):
    target = db.ReferenceProperty(Node, collection_name='reverse_edges')
    score = db.FloatProperty(default=0.0)

class Connection(Model):
    nodes = db.ListProperty(db.Key)
    score = db.FloatProperty(default=0.0)