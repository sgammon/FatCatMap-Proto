from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.services import ExtService
from momentum.fatcatmap.models.system import _ConfigGroup_


class DataEngine(PolyPro):
    enabled = db.BooleanProperty()


class Mapper(DataEngine):
    name = db.StringProperty()
    input_reader = db.StringProperty(choices=['datastore','datastore_key','blobstore_line','blobstore_zip'])
    handler = db.StringListProperty(indexed=False)
    params = db.StringListProperty(indexed=False)
    param_defaults = db.StringListProperty(indexed=False)


class DataEngineConfig(_ConfigGroup_):
    parent_ref = db.ReferenceProperty(DataEngine, collection_name='config')


class ServiceMapper(Mapper):
    service = db.ReferenceProperty(ExtService, collection_name='mappers')


class Pipeline(DataEngine):
    name = db.StringProperty()
    path = db.StringListProperty(indexed=False)
    async = db.BooleanProperty(default=False)


class ServicePipeline(Pipeline):
    service = db.ReferenceProperty(ExtService, collection_name='pipelines')


class Worker(DataEngine):
    name = db.StringProperty()
    worker_endpoint = db.StringProperty()


class ServiceWorker(Worker):
    service = db.ReferenceProperty(ExtService, collection_name='workers')


class WorkerMethod(PolyPro):
    name = db.StringProperty()