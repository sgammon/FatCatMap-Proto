import logging
import sunlightapi

from google.appengine.ext import db

from momentum.fatcatmap.pipelines.graph import GraphNode
from momentum.fatcatmap.pipelines.graph import NodeExtID
from momentum.fatcatmap.pipelines.sunlight import SunlightPipeline

from momentum.fatcatmap.models.geo import USState
from momentum.fatcatmap.models.geo import District
from momentum.fatcatmap.models.politics import LegislativeHouse
from momentum.fatcatmap.models.politics import UpperHouseDistrict
from momentum.fatcatmap.models.politics import LowerHouseDistrict


class SunlightLegislator(SunlightPipeline):

    def run(self, object=None, **kwargs):

        logging.info('Running sunlight legislator')

        if object is None:
            object = self.sunlight.legislators.get(**kwargs)
            legislator = object.__dict__

        else:
            legislator = object

        state = db.Key.from_path('USState', legislator['state'].upper())
        congress = db.Key.from_path('Legislature', 'us_congress')

        ## If we're adding a Senator...
        if legislator['title'].lower() == 'sen':

            ## Pull leg house and try to pull district
            legislative_house = LegislativeHouse.get_by_key_name('us_senate', parent=congress)
            seniority = legislator['district'].lower().split(' ')[0]
            district = District.get_by_key_name(legislator['state']+'-'+seniority[0].upper(), parent=legislative_house)

            ## Inject 'seniority' param to legislator Native object...
            legislator['seniority'] = seniority

            ## Create district if it doesn't exist...
            if district is None:
                district = UpperHouseDistrict(legislative_house, key_name=legislator['state']+'-'+seniority[0].upper())
                district.house = legislative_house
                district.state = state
                district.put()

        ## If we're adding a Congressperson..
        else:

            ## Pull leg house and try to pull district
            legislative_house = LegislativeHouse.get_by_key_name('us_house_of_reps', parent=congress)
            district = District.get_by_key_name(legislator['state']+'-'+legislator['district'], parent=legislative_house)

            ## Create district if it doesn't exist...
            if district is None:
                district = LowerHouseDistrict(legislative_house, key_name=legislator['state']+'-'+legislator['district'], number=int(legislator['district']), house=legislative_house)
                district.house = legislative_house
                district.state = state
                district.number = int(legislator['district'])
                district.put()

        ## Set references
        legislator['state'] = state
        legislator['district'] = district.key()
        legislator['house'] = legislative_house.key()
        legislator['party'] = db.Key.from_path('PoliticalParty', legislator['party'].upper())

        ## Calculate node label
        label = legislator['title']+'. '+legislator['firstname']+' '+legislator['lastname']+' ('+legislator['party'].name()+'-'+legislator['state'].name()+')'

        node = yield self.createNode(label, legislator)
        with self.pipeline.After(node):
            if 'bioguide_id' in legislator: yield NodeExtID(node, 'bioguide', 'bioguide_id', legislator['bioguide_id'])
            if 'votesmart_id' in legislator: yield NodeExtID(node, 'votesmart', 'votesmart_id', legislator['votesmart_id'])
            if 'fec_id' in legislator: yield NodeExtID(node, 'fec', 'fec_id', legislator['fec_id'])
            if 'govtrack_id' in legislator: yield NodeExtID(node, 'govtrack', 'govtrack_id', legislator['govtrack_id'])
            if 'crp_id' in legislator: yield NodeExtID(node, 'opensecrets', 'crp_id', legislator['crp_id'])
            if 'eventful_id' in legislator: yield NodeExtID(node, 'eventful', 'eventful_id', legislator['eventful_id'])
            if 'congresspedia_url' in legislator: yield NodeExtID(node, 'congresspedia', 'congresspedia_url', legislator['congresspedia_url'])
            if 'twitter_id' in legislator: yield NodeExtID(node, 'twitter', 'twitter_id', legislator['twitter_id'])
            if 'youtube_id' in legislator: yield NodeExtID(node, 'youtube', 'youtube_id', legislator['youtube_id'])


    def createNode(self, label, object):

        legislator_object = {

            'party':object.get('party', None),
            'house':object.get('house', None),
            'district':object.get('district', None),
            'first_name':object.get('firstname', None),
            'middle_name':object.get('middlename', None),
            'last_name':object.get('lastname', None),
            'name_suffix':object.get('name_suffix', None),
            'nickname':object.get('nickname', None),
            'gender':object.get('gender', 'u').lower(),
            'office_phone':object.get('phone', None),
            'office_fax':object.get('fax', None),
            'office_address':object.get('congress_address', None),
            'official_website':object.get('website', None),
            'official_webform':object.get('webform', None),
            'official_email':object.get('email', None)


        }

        return GraphNode('legislator', label, legislator_object)


class SunlightLegislators(SunlightPipeline):

    def run(self, **kwargs):

        logging.info('Beginning sunlight legislators')

        ## Get Legislators
        for legislator in self.sunlight.legislators.getList(**kwargs):
            logging.info('Yielding pipeline for legislator '+str(legislator))
            yield SunlightLegislator(legislator.__dict__)