from momentum.fatcatmap.models.sunlight import Legislator

from momentum.fatcatmap.pipelines.graph import Node
from momentum.fatcatmap.pipelines.graph import Edge
from momentum.fatcatmap.pipelines.opensecrets import CRPPipeline


class OpenSecretsContributorsSummary(CRPPipeline):


    def run(self, legislator=None, cid=None, cycle='2010'):

        if legislator is not None:
            pass

        elif cid is not None and legislator is None:

            ## Lookup legislator
            n = Node.get_by_ext_id('crp_id', cid)
            if n is None:
                legislator = yield SunlightLegislator(crp_id=cid)

            with self.pipelines.After(legislator):
                
                ## Make OpenSecrets request
                contributors = self.opensecrets.candContrib(cid=cid)

                for contributor in contributors:
                    contributor = yield Node()
                    with self.pipeline.After(contributor):
                        yield Edge()

