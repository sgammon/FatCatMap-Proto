import logging
import sunlightapi

from google.appengine.ext import db

from momentum.fatcatmap.models.graph import Node
from momentum.fatcatmap.pipelines.graph import Edge
from momentum.fatcatmap.pipelines.graph import NodeGroup
from momentum.fatcatmap.pipelines.graph import NodeExtID
from momentum.fatcatmap.pipelines.sunlight import SunlightPipeline
from momentum.fatcatmap.pipelines.sunlight.legislators import SunlightLegislator

from momentum.fatcatmap.models.group import GroupMembership
from momentum.fatcatmap.models.group import GroupRelationship

from momentum.fatcatmap.models.politics import JointCommittee
from momentum.fatcatmap.models.politics import LegislativeChamber
from momentum.fatcatmap.models.politics import LegislativeCommittee
from momentum.fatcatmap.models.politics import UpperChamberCommittee
from momentum.fatcatmap.models.politics import LowerChamberCommittee


class SunlightCommitteeMembership(SunlightPipeline):

	def run(self, group, committee, member):

		if 'crp_id' in member:
			legislator = Node.get_by_ext_id('crp_id', member['crp_id'])

		if legislator is None:
			legislator = yield SunlightLegislator(object=member)
			with self.pipeline.After(legislator):
				yield Edge('sunlight_committee_membership', [group, legislator], legislator=legislator, group=group)

		else:
			yield Edge('sunlight_committee_membership', [group, legislator], legislator=legislator, group=group)


class SunlightCommittee(SunlightPipeline):

	def run(self, id=None, object=None):

		logging.info('Running sunlight committee')

		if object is None:
			object = self.cache.get('sunlight-committee-'+str(id))
			if object is None:
				object = self.sunlight.committees.get(id)
				self.cache.set('sunlight-committee-'+str(id), object)

			committee = object.__dict__

			self.log.info('COMMITTEE OBJECT: '+str(object.__dict__))

		else:
			committee = object

		congress = db.Key.from_path('Legislature', 'us_congress')
		us_senate = db.Key.from_path('LegislativeChamber', 'us_senate', parent=congress)
		us_house = db.Key.from_path('LegislativeChamber', 'us_house_of_reps', parent=congress)

		## Resolve impl class
		if committee['chamber'].lower() == 'joint':
			committee['type'] = 'joint_legislative_committee'
			committee['chamber'] = [us_senate, us_house]

		elif committee['chamber'].lower() == 'senate':
			committee['type'] = 'upper_chamber_legislative_committee'
			committee['chamber'] = us_senate

		elif committee['chamber'].lower() == 'house':
			committee['type'] = 'lower_chamber_legislative_committee'
			committee['chamber'] = us_house

		## Set properties
		committee['code'] = committee['id']
		committee['legislature'] = congress

		## Calculate node label
		label = committee['name']

		node = yield self.createNode(label, committee)
		with self.pipeline.After(node):
			if 'id' in committee: yield NodeExtID(node, 'uscongress', 'jpsr_id', committee['id'])

		with self.pipeline.After(node):
			if 'subcommittees' in committee and len(committee['subcommittees']) > 0:
				for subcommittee in committee['subcommittees']:
					self.log.info('Yielding pipeline for subcommittee "'+str(subcommittee)+'".')
					#subcommittee['parent_committee'] = node
					yield SunlightCommittee(object=subcommittee)

		with self.pipeline.After(node):
			if 'members' in committee and len(committee['members']) > 0:
				for member in committee['members']:
					self.log.info('Creating membership for member "'+str(member)+'".')
					yield SunlightCommitteeMembership(node, node.native, member)


	def createNode(self, label, object):

		committee_object = {

		   'name': object.get('name', None),
		   'legislature': object.get('legislature', None),
		   'chamber': object.get('chamber', None),
			'code': object.get('id', None)

		}

		self.log.info('Creating node for committee ID '+str(committee_object['code']))

		return NodeGroup(object['type'], label, committee_object)


class SunlightCommittees(SunlightPipeline):

	def run(self, chamber):

		## Get Legislators
		for committee in self.sunlight.committees.getList(chamber):
			logging.info('Yielding pipeline for sunlight committee '+str(committee))

			committee = committee.__dict__
			subcommittees = []
			for item in committee['subcommittees']:
				subcommittees.append(item.__dict__)
			committee['subcommittees'] = subcommittees

			yield SunlightCommittee(object=committee)