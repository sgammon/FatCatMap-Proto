from momentum.fatcatmap.api.data import MomentumDataAPI
from momentum.fatcatmap.api.data import MomentumDataAPIResponse


class QueryResponse(MomentumDataAPIResponse):
    uuid = None
    cursor = None


class QueryAction(MomentumDataAPI):

    response = QueryResponse