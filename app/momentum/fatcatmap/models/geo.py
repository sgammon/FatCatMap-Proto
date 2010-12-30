from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro


class USState(Model):
    fullname = db.StringProperty()
    abbreviation = db.StringProperty()


class District(PolyPro):
    state = db.ReferenceProperty(USState, collection_name='districts')