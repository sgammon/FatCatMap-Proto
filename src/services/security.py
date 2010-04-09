import logging
import wsgiref.handlers
from pyamf.remoting.gateway.wsgi import WSGIGateway
from google.appengine.api import users

class Security:  
    
    def getuser(self):
        user = users.get_current_user()
        if user:
            logging.info('User is logged in.')
            if users.is_current_user_admin():
                result = {'result':'loggedin','nickname':str(user.nickname()+' (Admin)')}
                logging.info(str(result))
                return result
            else:
                result = {'result':'loggedin','nickname':str(user.nickname())}
                logging.info(str(result))
                return result
        else:
            logging.info('User is anonymous.')
            result = {'result':'anonymous'}
            logging.info(str(result))
            return result
        
def auth(username, password):
    return True

services = {
            'security':Security,
}

def main():
    application = WSGIGateway(services,authenticator=auth)
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == '__main__':
    main()                