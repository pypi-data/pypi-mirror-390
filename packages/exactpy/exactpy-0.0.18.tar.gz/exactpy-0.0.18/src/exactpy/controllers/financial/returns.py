from exactpy.controllers.base import BaseController
from exactpy.models.financial import (
    ReturnModel,
)


class ReturnController(BaseController):
    _resource = "read/financial/Returns"
    _model = ReturnModel
