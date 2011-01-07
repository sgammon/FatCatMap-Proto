import config
import logging

from tipfy import import_string
from tipfy import cached_property

from momentum.fatcatmap.api import MomentumAPIRequest
from momentum.fatcatmap.handlers import FCMBaseRequestHandler


class CheshireDispatch(FCMBaseRequestHandler):

    config = {}
    adapter = None
    api_request = None


    def handleRequest(self, request):

        self.api_request = request

        ## Resolve method
        func = self.resolveMethod(self.api_request.method)


    def decodeRequest(self, *args, **kwargs):

        self.config = self.gatherConfig()

        ## Load Adapter
        if 'format' in config:
            if config['format'].lower() in self.apiConfig['adapters']:
                if self.apiConfig['adapters'][config['format'].lower()]['enabled'] != True:

                    if self.apiConfig['debug'] == True:
                        logging.warning('Invalid output adapter encountered: "'+str(config['output'].lower())+'". Responding with error.')
                    raise FormatDisabled
                else:
                    self.loadDataAdapter(self.apiConfig['adapters'][config['format'].lower()]['path'])
            else:
                raise FormatInvalid
        else:
            self.loadDataAdapter(self.apiConfig['adapters']['default'])

        ## Decode Payload
        self.api_request = MomentumAPIRequest.spawnRequest(self.config, self.adapter)

        ## Resolve method
        self.computed_method = self.resolveMethod()


    def gatherConfig(self, **kwargs):
        temp_config = {}

        ## Combine GET Args
        if len(self.request.args) > 0:
            for key, value in self.request.args.items():
                temp_config[key] = value

        ## Combine POST Params
        if len(self.request.form) > 0:
            for key, value in self.request.form.items():
                temp_config[key] = value

        ## Combine URL segments
        if len(kwargs) > 0:
            for key, value in kwargs.items():
                temp_config[key] = value

        return temp_config


    def loadDataAdapter(self, path_or_name):

        if isinstance(path_or_name, basestring):
            if path_or_name in self.apiConfig['adapters']:
                self.adapter = import_string('.'.join(self.apiConfig['adapters'][path_or_name]['path']))()
        elif isinstance(path_or_name, list):
            self.adapter = import_string('.'.join(path_or_name))()


    def resolveMethod(self):

        if len(self.api_request.method)


    @cached_property
    def apiConfig(self):
        return config.config.get('momentum.fatcatmap.api')


    def get(self, *args, **kwargs): return self.handleRequest(self.decodeRequest(*args, **kwargs))
    def put(self, *args, **kwargs): return self.handleRequest(self.decodeRequest(*args, **kwargs))

    def post(self, *args, **kwargs): return self.handleRequest(self.decodeRequest(*args, **kwargs))
    def head(self, *args, **kwargs): return self.handleRequest(self.decodeRequest(*args, **kwargs))
    def delete(self, *args, **kwargs): return self.handleRequest(self.decodeRequest(*args, **kwargs))
    def options(self, *args, **kwargs): return self.handleRequest(self.decodeRequest(*args, **kwargs))


### API Exceptions
class APIException(Exception): message = 'An error was encountered while processing your request. Please try again later.'

class OutputException(APIException): message = 'An error was encountered during response encoding. Please try again.'
class FormatInvalid(OutputException): message = 'The specified output type is not supported. Please rewrite your request and try again.'
class FormatDisabled(OutputException): message = 'The specified output type is currently disabled. Please rewrite your request and try again.'

class MethodException(APIException): message = 'An error was encountered trying to find or complete the requested method. Please try again later.'
class InvalidMethod(MethodException): message = 'The requested method could not be found. Please try again.'