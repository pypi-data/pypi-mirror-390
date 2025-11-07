from exactpy.controllers.base import BaseController
from exactpy.models.financial import ProfitLossOverviewModel


class ProfitLossOverviewController(BaseController):
    _resource = "read/financial/ProfitLossOverview"
    _model = ProfitLossOverviewModel
