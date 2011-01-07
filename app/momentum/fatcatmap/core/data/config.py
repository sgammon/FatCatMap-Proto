from google.appengine.ext import db

from momentum.fatcatmap.core.data import FCMModelMixin

from momentum.fatcatmap.models.system import _ConfigGroup_
from momentum.fatcatmap.models.system import _ConfigParam_


class ConfigMixin(FCMModelMixin):

	def setConfig(self, groupname, values={}, **kwargs):
		pass


	def setConfigParam(self, groupname, key, value):
		pass


	def getConfig(self, groupname):
		pass


	def getConfigGroups(self):
		pass