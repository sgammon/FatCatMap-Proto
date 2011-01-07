from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.system import _ConfigGroup_


#### ==== Service Models ==== ####
class ExtService(Model):
    name = db.StringProperty()
    description = db.TextProperty()
    homepage = db.LinkProperty()

class ExtServiceKey(Model):
    name = db.StringProperty()
    value = db.StringProperty()
    service = db.ReferenceProperty(ExtService, collection_name='keys')
    last_used = db.DateTimeProperty()
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


#### ==== Config Storate ==== ####
class ExtServiceConfig(_ConfigGroup_):
    parent_ref = db.ReferenceProperty(ExtService, collection_name='config')


#### ==== External ID Models ==== ####
class ExtID(PolyPro):
    name = db.StringProperty(default=None)
    value = db.StringProperty()
    link = db.LinkProperty()
    service = db.ReferenceProperty(ExtService, collection_name='consumed_objects')

class NodeID(ExtID):
    pass
    
class EdgeID(ExtID):
    pass