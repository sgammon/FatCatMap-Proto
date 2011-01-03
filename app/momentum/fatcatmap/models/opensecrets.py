from google.appengine.ext import db

from momentum.fatcatmap.models.graph import DirectedEdge
from momentum.fatcatmap.models.industry import Organization
from momentum.fatcatmap.models.politics import ElectionCycle


class CampaignContribution(DirectedEdge):
    pass


class CampaignContributor(Organization):
    pass