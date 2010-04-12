import logging, settings
import wsgiref.handlers
from pyamf.remoting.gateway.wsgi import WSGIGateway
from google.appengine.ext import db
from google.appengine.api import users, memcache
from models import Donation, Candidate, Contributor, OSum

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


def mapObject(object,parent=None,root=False,depth_limit=2,climit=7,depth=0,omit_list=[]):
    
    ############################ INDENT ############################
    if settings.map_object_logging: logging.info('     ')
    indent = '-'
    for i in range(0,depth):
        indent = indent+'-----'
    
    if settings.map_object_logging: logging.info(indent+'MapObject: Requested '+str(object)+' at depth '+str(depth))
    
    opt = str(depth_limit)+'::'+str(climit)
    
    if settings.map_object_logging: logging.info(indent+'--parent: '+str(parent))
    if settings.map_object_logging: logging.info(indent+'--omit list: '+str(omit_list))
    
    if isinstance(object, db.Key) or isinstance(object, basestring):
        if settings.map_object_logging: logging.info(indent+'--object is a simple key. converting to object.')
        object = db.get(object)
    
    if str(object.key()) in struct_cache:
        if opt in struct_cache[str(object.key())]:
            if settings.map_object_logging: logging.info(indent+'--found object in struct cache at opt: '+opt+'. returning.')
            return struct_cache[str(object.key())][opt]
        
    m = memcache.get('map_cache::'+str(object.key())+'::'+opt)
    if m is not None:
        if settings.map_object_logging: logging.info(indent+'--found object in memcache at key: '+'map_cache::'+str(object.key())+'::'+opt+'. returning.')
        return m
    
    res = {}
    res['key'] = str(object.key())
    res['object'] = todict(object)
    res['object']['key'] = str(object.key())
    res['object']['kind'] = str(object.kind())
    res['object']['connections'] = []
    res['kind'] = str(object.kind())
    res['display_text'] = str(object.display_text)
    res['is_root'] = str(root)


    if depth < depth_limit:
        
        if settings.map_object_logging: logging.info(indent+'--depth greater than zero. mapping:')
        
        summary = OSum.get_by_key_name(str(object.key()))
        if summary is None:
            
            donations = Donation.gql("WHERE "+str(object.kind()).lower()+" = :1 ORDER BY amount DESC",object)
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
                if db.Key(connection) in omit_list:
                    if settings.map_object_logging: logging.info(indent+'--connection: '+str(connection))
                    continue
                else:
                    if parent is not None:
                        res['object']['connections'].append(mapObject(connection,object,False,depth_limit,climit,depth+1,[parent.key(),object.key()]))
                    else:
                        res['object']['connections'].append(mapObject(connection,object,False,depth_limit,climit,depth+1,[object.key()]))
                    i = i+1
                
                
        else:
            if settings.map_object_logging: logging.info(indent+'--found OSum: '+str(object.key()))
            for connection in summary.connections:
                if connection in omit_list:
                    continue
                else:
                    if parent is not None:
                        res['object']['connections'].append(mapObject(connection,object,False,depth_limit,climit,depth+1,[parent.key(),object.key()]))
                    else:
                        res['object']['connections'].append(mapObject(connection,object,False,depth_limit,climit,depth+1,[object.key()]))
                        
        
    struct_cache[str(object.key())] = {opt:res}
    memcache.set('map_cache::'+str(object.key())+'::'+opt,res,time=7200)
    return res

class FatCatData:  

    def RetrieveConnectionsByKey(self,key):
        
        memkey = 'map::key_'+key+'::depth_4::climit_9'
        map = memcache.get(memkey)
        if map is None:
            map = mapObject(key,None,True,4,9)
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
        map = None
        if map is None:
            map = mapObject(c,None,True,1,9)
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