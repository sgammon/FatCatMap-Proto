import sunlightapi
from momentum.fatcatmap.pipelines import FCMPipeline

sunlight_object = None


class SunlightPipeline(FCMPipeline):

    service = 'sunlight'
    sunlight = None

    def pre_execute(self):

        global sunlight_object
        if sunlight_object is None:
            sunlight_object = sunlightapi.sunlight
            sunlight_object.apikey = self.service['keys'][0].value
        self.sunlight = sunlight_object