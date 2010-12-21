from google.appengine.ext import db
from momentum.fatcatmap.core.data import FCMModelMixin

from momentum.fatcatmap.core.data.properties.security import UserReferenceProperty


class CreatedModifiedMixin(FCMModelMixin):
	
	''' Automatically appends createdAt and modifiedAt values to a model. These values are derived on put(). '''
	
	modifiedAt = db.DateTimeProperty(auto_now=True)
	createdAt = db.DateTimeProperty(auto_now_add=True)
	
	
class UserAuditMixin(FCMModelMixin):
	
	modifiedBy = UserReferenceProperty(auto_current_user=True)
	createdBy = UserReferenceProperty(auto_current_user_add=True)