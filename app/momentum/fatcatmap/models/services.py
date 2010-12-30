from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.graph import Node
from momentum.fatcatmap.models.graph import Edge


#### ==== Service Models ==== ####
class ExtService(Model):
    name = db.StringProperty()
    description = db.TextProperty()
    homepage = db.LinkProperty()

class ExtServiceKey(Model):
    name = db.StringProperty()
    value = db.StringProperty()
    service = db.ReferenceProperty(ExtService, collection_name='keys')
    global_uses = db.IntegerProperty()
    enforce_limits = db.BooleanProperty()
    global_usage_limit = db.IntegerProperty()
    daily_usage_limit = db.IntegerProperty()

class ExtInteraction(PolyPro):
    method = db.StringProperty()
    result = db.StringProperty(choices=['success','failure'])
    request = db.BlobProperty()
    response = db.BlobProperty()
    service = db.ReferenceProperty()
    timestamp = db.DateTimeProperty(auto_now_add=True)
    enable_caching = db.BooleanProperty()


#### ==== External ID Models ==== ####
class ExtID(PolyPro):
    name = db.StringProperty()
    value = db.StringProperty()
    link = db.LinkProperty()
    service = db.ReferenceProperty(ExtService, collection_name='consumed_objects')

class NodeID(ExtID):
    node = db.ReferenceProperty(Node, collection_name='ext_ids')
    
class EdgeID(ExtID):
    edge = db.ReferenceProperty(Edge, collection_name='ext_ids')