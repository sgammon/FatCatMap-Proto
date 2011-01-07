from momentum.fatcatmap.api import MomentumAPI
from momentum.fatcatmap.api import MomentumAPIResponse


### ==== Momentum Data API ==== ###
class MomentumDataAPI(MomentumAPI):
    pass


##### ==== Data API Response Prototypes ==== #####
class MomentumDataAPIResponse(MomentumAPIResponse):
    pass


class DataOperationResponse(MomentumDataAPIResponse):
    key = None