import logging
import wsgiref.handlers
import pyamf
from pyamf.remoting.gateway.wsgi import WSGIGateway
from google.appengine.ext import db
from google.appengine.api import users, memcache
from models import *

struct_cache = {}

def todict(obj):
    props = obj.properties()
    dprops = obj.dynamic_properties()

    res = {}

    for prop in props:        
        res[prop] = obj.__getattribute__(prop)

    for prop in dprops:
        res[prop] = obj.__getattribute__(prop)

    return res

def mapObject(object,root=False,depth=2,climit=7):
    
    logging.info('------------MapObject: '+str(object))
    
    opt = str(depth)+'::'+str(climit)
    
    if isinstance(object, db.Key) or isinstance(object, basestring):
        object = db.get(object)
    
    if str(object.key()) in struct_cache:
        if opt in struct_cache[str(object.key())]:
            return struct_cache[str(object.key())][opt]
        
    m = memcache.get('map_cache::'+str(object.key())+'::'+opt)
    if m is not None:
        return m
    
    res = {}
    res['key'] = str(object.key())
    res['object'] = todict(object)
    res['object']['kind'] = str(object.kind())
    res['object']['connections'] = []
    res['kind'] = str(object.kind())
    res['display_text'] = str(object.display_text)
    res['is_root'] = str(root)


    if depth > 0:
        
        summary = OSum.get_by_key_name(str(object.key()))
        if summary is None:
            
            donations = db.GqlQuery("SELECT * FROM Donation WHERE "+str(object.kind()).lower()+" = :1 ORDER BY amount DESC",object)
            donations = donations.fetch(donations.count())
            connections = {}
            
            i = 0
            
            for donation in donations:
                if i == climit: break
                
                if str(object.kind()) == 'Candidate': fk = donation.contributor
                elif str(object.kind()) == 'Contributor': fk = donation.candidate
                
                if str(fk.key()) not in connections:
                    connections[str(fk.key())] = fk
                    
                i = i+1
                
            for connection in connections:
                res['object']['connections'].append(mapObject(connection,False,depth-1,climit))
                i = i+1
                
                
        else:
            for connection in summary.connections:
                res['object']['connections'].append(mapObject(connection,False,depth-1,climit))
                        
        
    struct_cache[str(object.key())] = {opt:res}
    memcache.set('map_cache::'+str(object.key())+'::'+opt,res,time=7200)
    
    return res

class FatCatData:  

    def RetrieveConnectionsByKey(self,key):
        
        memkey = 'map::key_'+key+'::depth_4::climit_9'
        map = memcache.get(memkey)
        if map is None:
            map = mapObject(key,True,4,9)
            memcache.set(memkey,map,time=7200)
            
        return {'result':'success','response':map}
        
    
    def RetrieveFirstGraph(self):
        
        c = memcache.get('initial_graph_seed')
        if c is None:
            c = Candidate.all()
            c = c.fetch(1)
            c = c[0]
            memcache.set('initial_graph_seed',c,time=7200)
            
        memkey = 'map::key_'+str(c.key())+'::depth_4::climit_9'
        map = memcache.get(memkey)
        if map is None:
            map = mapObject(c,True,3,9)
            memcache.set(memkey,map,time=7200)
        return {'result':'success','response':map}
    
        
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