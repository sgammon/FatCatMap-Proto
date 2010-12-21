from tornado.web import RequestHandler, asynchronous

class JSONRPCRequestHandler(RequestHandler):

    SUPPORTED_METHODS = ("POST",)

    def __init__(self, application, request, dispatcher=None, **kwargs):
        assert dispatcher, 'dispatcher is required'
        super(JSONRPCRequestHandler, self).__init__(
            application, request, **kwargs)
        self.dispatcher = dispatcher

    def post(self):
        response = self.dispatcher.dispatch(self.request.body)
        self.set_header('Content-Type', 'application/json')
        self.write(response)
        self.finish()



