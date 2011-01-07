from momentum.fatcatmap.api.data import MomentumDataAPI
from momentum.fatcatmap.api.data import MomentumDataAPIResponse


class DataRetrieveResponse(MomentumDataAPIResponse):
    pass


class GetAction(MomentumDataAPI):

    response = DataRetrieveResponse