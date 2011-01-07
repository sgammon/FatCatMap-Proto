from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.models.graph import Native


class Industry(Model):
    pass


class Organization(Native):
    name = db.StringProperty()