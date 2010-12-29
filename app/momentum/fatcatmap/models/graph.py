from google.appengine.ext import db

from ProvidenceClarity.data.core.model import Model
from ProvidenceClarity.data.core.polymodel import PolyPro



class Node(Model):
	label = db.StringProperty()
	
	
class Edge(Model):
	nodes = db.ListProperty(db.Key)
	

class Graph(Model):
	name = db.StringProperty()