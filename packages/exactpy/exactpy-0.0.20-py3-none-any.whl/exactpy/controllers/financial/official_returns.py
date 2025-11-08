from exactpy.controllers.base import BaseController
from exactpy.models.financial import OfficialReturnModel


class OfficialReturnController(BaseController):
    _resource = "financial/OfficialReturns"
    _model = OfficialReturnModel
