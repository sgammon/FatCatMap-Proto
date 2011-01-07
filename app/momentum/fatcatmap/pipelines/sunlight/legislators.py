import hashlib
import logging
import sunlightapi

from google.appengine.ext import db
from google.appengine.api import taskqueue

from momentum.fatcatmap.pipelines.graph import Node
from momentum.fatcatmap.pipelines.graph import NodeExtID
from momentum.fatcatmap.pipelines.sunlight import SunlightPipeline

from momentum.fatcatmap.pipelines.opensecrets.contributions import OpenSecretsContributorsSummary

from momentum.fatcatmap.models.geo import USState
from momentum.fatcatmap.models.geo import District
from momentum.fatcatmap.models.politics import LegislativeChamber
from momentum.fatcatmap.models.politics import UpperChamberDistrict
from momentum.fatcatmap.models.politics import LowerChamberDistrict


class SunlightLegislator(SunlightPipeline):

    def run(self, object=None, **kwargs):

        if object is None:

            md5_kwargs = hashlib.md5()
            md5_kwargs.update(str(kwargs))
            cache_key = 'sunlight-legislator-'+md5_kwargs.hexdigest()
            object = self.cache.get(cache_key)

            if object is None:
                object = self.sunlight.legislators.get(**kwargs)
                self.cache.set(cache_key, object)

            legislator = object.__dict__

        else:
            legislator = object

        state = db.Key.from_path('USState', legislator['state'].upper())
        congress = db.Key.from_path('Legislature', 'us_congress')

        ## If we're adding a Senator...
        if legislator['chamber'].lower() == 'senate':

            ## Pull leg house and try to pull district
            legislative_house = self.cache.get('legislative-chamber-us-senate')
            if legislative_house is None:
                legislative_house = LegislativeChamber.get_by_key_name('us_senate', parent=congress)
                self.cache.set('legislative-chamber-us-senate', legislative_house)

            seniority = legislator['district'].lower().split(' ')[0]

            cache_key = 'legislative-district-'+str(legislative_house.key())+'-'+legislator['state']+'-'+seniority[0].upper()
            district = self.cache.get(cache_key)
            if district is None:
                district = District.get_by_key_name(legislator['state']+'-'+seniority[0].upper(), parent=legislative_house)

                ## Create district if it doesn't exist...
                if district is None:
                    district = UpperChamberDistrict(legislative_house, key_name=legislator['state']+'-'+seniority[0].upper())
                    district.house = legislative_house
                    district.state = state
                    district.put()

                self.cache.set(cache_key, district)

            ## Inject 'seniority' param to legislator Native object...
            legislator['seniority'] = seniority


        ## If we're adding a Congressperson..
        elif legislator['chamber'].lower() == 'house':

            ## Pull leg house and try to pull district
            legislative_house = self.cache.get('legislative-chamber-us-house-of-reps')
            if legislative_house is None:
                legislative_house = LegislativeChamber.get_by_key_name('us_house_of_reps', parent=congress)
                self.cache.set('legislative-chamber-us-house-of-reps', legislative_house)


            cache_key = 'legislative-district-'+str(legislative_house.key())+'-'+legislator['state']+'-'+legislator['district']
            district = self.cache.get(cache_key)
            if district is None:
                district = District.get_by_key_name(legislator['state']+'-'+legislator['district'], parent=legislative_house)

                ## Create district if it doesn't exist...
                if district is None:
                    district = LowerChamberDistrict(legislative_house, key_name=legislator['state']+'-'+legislator['district'], number=int(legislator['district']), house=legislative_house)
                    district.chamber = legislative_house
                    district.state = state
                    district.number = int(legislator['district'])
                    district.put()

                self.cache.set(cache_key, district)

        ## Set references
        legislator['state'] = state
        legislator['district'] = district.key()
        legislator['house'] = legislative_house.key()
        legislator['party'] = db.Key.from_path('PoliticalParty', legislator['party'].upper())

        ## Calculate node label
        label = legislator['title']+'. '+legislator['firstname']+' '+legislator['lastname']+' ('+legislator['party'].name()+'-'+legislator['state'].name()+')'

        node = yield self.createNode(label, legislator)
        with self.pipeline.After(node):
            if 'bioguide_id' in legislator and legislator['bioguide_id'] != '': yield NodeExtID(node, 'bioguide', 'bioguide_id', legislator['bioguide_id'])
            if 'votesmart_id' in legislator and legislator['votesmart_id'] != '': yield NodeExtID(node, 'votesmart', 'votesmart_id', legislator['votesmart_id'])
            if 'fec_id' in legislator and legislator['fec_id'] != '': yield NodeExtID(node, 'fec', 'fec_id', legislator['fec_id'])
            if 'govtrack_id' in legislator and legislator['govtrack_id'] != '': yield NodeExtID(node, 'govtrack', 'govtrack_id', legislator['govtrack_id'])
            if 'eventful_id' in legislator and legislator['eventful_id'] != '': yield NodeExtID(node, 'eventful', 'eventful_id', legislator['eventful_id'])
            if 'congresspedia_url' in legislator and legislator['congresspedia_url'] != '': yield NodeExtID(node, 'congresspedia', 'congresspedia_url', legislator['congresspedia_url'])
            if 'twitter_id' in legislator and legislator['twitter_id'] != '': yield NodeExtID(node, 'twitter', 'twitter_id', legislator['twitter_id'])
            if 'youtube_id' in legislator and legislator['youtube_id'] != '': yield NodeExtID(node, 'youtube', 'youtube_id', legislator['youtube_id'])
            if 'crp_id' in legislator and legislator['crp_id'] != '':
                yield NodeExtID(node, 'opensecrets', 'crp_id', legislator['crp_id'])
                yield OpenSecretsContributorsSummary(node, legislator['crp_id'])


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

        return Node('legislator', label, legislator_object)


class SunlightLegislatorsByState(SunlightPipeline):

    def run(self, state):

        legislators = self.sunlight.legislators.getList(state=state)

        for legislator in legislators:

            leg_cfg = {'crp_id':legislator.__dict__['crp_id']}
            md5_hash = hashlib.md5()
            md5_hash.update(str(leg_cfg))

            self.cache.set('sunlight-legislator-'+md5_hash.hexdigest(), legislator)
            yield SunlightLegislator(crp_id=legislator.__dict__['crp_id'])


class SunlightLegislators(SunlightPipeline):

    def run(self, **kwargs):

        if len(kwargs) == 0:
            states = USState.all().fetch(50)
            for state in states:
                yield SunlightLegislatorsByState(state.key().name())
        else:

            ## Get Legislators
            legislators = self.sunlight.legislators.getList(**kwargs)

            for legislator in legislators:

                ## Cache legislator
                leg_cfg = {'crp_id':legislator.__dict__['crp_id']}
                md5_hash = hashlib.md5()
                md5_hash.update(str(leg_cfg))

                self.cache.set('sunlight-legislator-'+md5_hash.hexdigest(), legislator)
                yield SunlightLegislator(crp_id=legislator.__dict__['crp_id'])