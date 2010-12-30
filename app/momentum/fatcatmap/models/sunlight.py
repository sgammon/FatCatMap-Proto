from google.appengine.ext import db

from momentum.fatcatmap.models.person import RoleMapping


class Legislator(RoleMapping):

    in_office = db.BooleanProperty()

    office_phone = db.PhoneNumberProperty()
    office_fax = db.PhoneNumberProperty()
    office_address = db.PostalAddressProperty()
    
    official_website = db.LinkProperty()
    official_webform = db.LinkProperty()
    official_email = db.EmailProperty()