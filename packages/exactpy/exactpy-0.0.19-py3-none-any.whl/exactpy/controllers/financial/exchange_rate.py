from exactpy.controllers.base import BaseController
from exactpy.models.financial import ExchangeRateModel


class ExchangeRateController(BaseController):
    _resource = "financial/ExchangeRates"
    _model = ExchangeRateModel
