import crpapi
from momentum.fatcatmap.pipelines import FCMPipeline

crp_object = None


class CRPPipeline(FCMPipeline):

    opensecrets = None
    service = 'opensecrets'
    queue_name = 'sunlight-worker'

    def pre_execute(self):

        global crp_object
        if crp_object is None:
            crp_object = crpapi.CRP
            crp_object.apikey = self.service['keys'][0].value
        self.opensecrets = crp_object