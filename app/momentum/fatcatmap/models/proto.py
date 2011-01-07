from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.system import _Counter_
from momentum.fatcatmap.models.system import _ConfigGroup_


class Prototype(Model):
    pass


class PrototypeProperty(Model):
    pass


class PrototypeConfig(_ConfigGroup_):
    parent_ref = db.ReferenceProperty(Prototype, collection_name='config')


class PrototypeCounter(_Counter_):
    pass