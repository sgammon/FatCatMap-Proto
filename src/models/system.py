from google.appengine.ext import db
from google.appengine.ext.db import polymodel

class StoredImage(db.Model):
    key = db.StringProperty(indexed=True)
    content = db.BlobProperty()
    mimetype = db.StringProperty()
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty(auto_current_user_add=True)
    
class UserAvatar():
    user = db.UserProperty(indexed=True)
    image = db.ReferenceProperty(StoredImage)
    
class Search(db.Model):
    user = db.UserProperty(indexed=True)
    term = db.StringProperty(indexed=True)