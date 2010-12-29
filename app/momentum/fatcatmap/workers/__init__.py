from momentum.fatcatmap.handlers import FCMRequestHandler


class FCMWorker(FCMRequestHandler):

    ## Universal params
    params = None

    def __init__(self, *args, **kwargs):

        self.params = {}
        super(FCMWorker, self).__init__(*args, **kwargs)

        ## Copy GET vars to params
        for key, value in self.request.args.items():
            self.params[key] = value

        ## Copy POST vars to params
        for key, value in self.request.form.items():
            self.params[key] = value


    ## Map HTTP methods to 'execute'
    def get(self, **kwargs): return self.execute(**kwargs)
    def post(self, **kwargs): return self.execute(**kwargs)