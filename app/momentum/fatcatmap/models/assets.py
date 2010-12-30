from google.appengine.ext import db
from google.appengine.ext import blobstore

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro


#### ==== Models for data groupings/sources ==== ####
class DataStub(PolyPro):
    version = db.FloatProperty()

class DatastoreData(DataStub):
    data = db.BlobProperty()

class DatastoreGroup(DataStub):
    data = db.ListProperty(db.Key)

class BlobstoreData(DataStub):
    data = blobstore.BlobReferenceProperty()

class ExternalData(DataStub):
    data = db.LinkProperty()


#### ==== Asset Models ==== ####
class StoredAsset(PolyPro):
    filename = db.SringProperty()
    size = db.IntegerProperty()
    mime_type = db.StringProperty(default='application/octet-stream')
    storage_type = db.StringProperty(choices=['datastore','blobstore','external'])
    storage_data = db.ReferenceProperty(DataStub, collection_name='assets')

class StyleAsset(StoredAsset):
    pass

class ScriptAsset(StoredAsset):
    pass

class ImageAsset(StoredAsset):
    # Image Properties
    width = db.IntegerProperty()
    height = db.IntegerProperty()

    # Fast Serving
    fast_serving = db.BooleanProperty(default=False)
    fast_serving_url = db.LinkProperty()