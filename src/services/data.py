import logging
import wsgiref.handlers
import pyamf
from pyamf.remoting.gateway.wsgi import WSGIGateway
from google.appengine.ext import db
from google.appengine.api import users
from models import *

def todict(obj):
    props = obj.properties()
    dprops = obj.dynamic_properties()

    res = {}

    for prop in props:        
        res[prop] = obj.__getattribute__(prop)

    for prop in dprops:
        res[prop] = obj.__getattribute__(prop)

    return res

def mapObject(key,root=False,depth=2,climit=7):
    
    res = {}
    object = db.get(key)
    
    res['key'] = str(object.key())
    res['object'] = todict(object)
    res['object']['kind'] = str(object.kind())
    res['object']['is_root'] = str(root)
    res['kind'] = str(object.kind())
    res['is_root'] = str(root)
    res['connections'] = {}
    
    if depth>0:
        
        if str(object.kind()) == 'Contributor':
            donations = db.GqlQuery("SELECT * FROM Donation WHERE candidate = :candidate ORDER BY amount DESC",candidate=object)
            
            candidates = []
            
            for donation in donations:
                pass
                
            for candidate in candidates:
                res['connections'][str(candidate.key())] = mapObject(str(candidate.key()),False,depth-1,climit)
            
        elif str(object.kind()) == 'Candidate':
            donations = db.GqlQuery("SELECT * FROM Donation WHERE contributor = :contributor ORDER BY amount DESC",contributor=object)
            
            contributors = {}
            
            i = 0
            for donation in donations:
                if i == climit:
                    break
                try:
                    t = contributors[str(donation.contributor.key())]
                except KeyError, BadValueError:
                    contributors[str(donation.contributor.key())] = donation.contributor
                    i = i+1
            
            for contributor in contributors:
                res['connections'][str(contributor.key())] = mapObject(str(contributor.key()),False,depth-1,climit)
                
    return res

class FatCatData:  

    def RetrieveConnectionsByKey(self,key):
        
        map = mapObject(key,True,2,7)
        return {'result':'success','response':map}
        
    
    def RetrieveFirstGraph(self):
        
        
        c = Candidate.all()
        c = c.fetch(1)
        c = c[0]
        connections = {}
        
        d = Donation.gql("WHERE candidate = :1 ORDER BY amount DESC",c)
        d = d.fetch(9)
        
        for donation in d:
        
            try:
                var = connections[str(donation.contributor.key())]
            except KeyError:
                connections[str(donation.contributor.key())] = {'kind':'Contributor','is_root':'false','orgname':str(donation.contributor.orgname),'key':str(donation.contributor.key()),'display_text':str(donation.contributor.display_text),'contributions':[]}
                        
            connections[str(donation.contributor.key())]['contributions'].append({'key':str(donation.key()),'amount':str(donation.amount)})
        
        res = {'result':'success','response':{}}
        
        res['response']['root'] = todict(c)
        res['response']['root_type'] = 'candidate'
        res['response']['connections'] = connections        
        res['response']['root']['key'] = str(c.key())
        res['response']['root']['kind'] = 'Candidate'
        res['response']['root']['is_root'] = 'true'           
        
        return res
        
        
        #c = Candidate.all()
        #c = c.fetch(1)
        
        #c = c[0]
        
        #map = mapObject((c.key()),True,2,9)
        #return {'result':'success','response':map}
    
        
    def RetrieveConnectionsByText(self,sterm):
        pass
        
def auth(username, password):
    return True

services = {
            'data':FatCatData,
}

def main():
    application = WSGIGateway(services,authenticator=auth)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()