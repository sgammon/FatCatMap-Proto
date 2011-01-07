from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.system import _Counter_
from momentum.fatcatmap.models.system import _ConfigGroup_

from momentum.fatcatmap.models.services import NodeID
from momentum.fatcatmap.models.services import EdgeID


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

    @classmethod
    def get_by_ext_id(id_name, id_value):
        n = NodeID.all().filter('name =', id_name).filter('value =', id_value).get()
        if n is None or len(n) == 0:
            return None
        else:
            return db.get(n.parent())

class Native(PolyPro):
    version = db.IntegerProperty(default=1)
    node = db.ReferenceProperty(Node, collection_name='native')


#### ==== Models for Node Relationships ==== ####
class EdgeType(Model):
    name = db.StringProperty()
    plural = db.StringProperty()
    edge_text = db.StringProperty()
    description = db.TextProperty()
    edge_impl_class = db.StringListProperty(indexed=False)

class SuperEdge(Model):
    score = db.FloatProperty(default=0.0)
    target = db.ListProperty(db.Key)
    partner = db.ListProperty(db.Key)
    connection = db.ListProperty(db.Key)
    
class Edge(PolyPro):
    score = db.FloatProperty(default=0.1)
    type = db.ReferenceProperty(EdgeType, collection_name='edges')
    source = db.ReferenceProperty(Node, collection_name='outgoing_edges')
    target = db.ReferenceProperty(Node, collection_name='incoming_edges')
    partner = db.SelfReferenceProperty()
    connection = db.ReferenceProperty(SuperEdge, collection_name='edges')

class UndirectedEdge(Edge):
    pass

class DirectedEdge(Edge):
    is_source = db.BooleanProperty()

class DistantEdge(Edge):
    pass


#### ==== Config Models ==== ####
class NodeTypeConfig(_ConfigGroup_):
    parent_ref = db.ReferenceProperty(NodeType, collection_name='config')

class EdgeTypeConfig(_ConfigGroup_):
    parent_ref = db.ReferenceProperty(EdgeType, collection_name='config')


#### ==== Counter Models ==== ####
class NodeTypeCounter(_Counter_):
    pass

class EdgeTypeCounter(_Counter_):
    pass