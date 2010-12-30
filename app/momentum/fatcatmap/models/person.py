from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro

from momentum.fatcatmap.graph import Natural


class Role(Model):
    name = db.StringProperty()


class Person(Natural):

    first_name = db.StringProperty()
    middle_name = db.StringProperty()
    last_name = db.StringProperty()
    name_suffix = db.StringProperty()
    nickname = db.StringProperty()
    gender = db.StringProperty(choices=['m','f'])


class RoleMapping(PolyPro):

    role = db.ReferenceProperty(Role, collection_name='mappings')
    person = db.ReferenceProperty(Person, collection_name='roles')
    current = db.BooleanProperty(default=True)

    start_date = db.DateTimeProperty()
    end_date = db.DateTimeProperty()