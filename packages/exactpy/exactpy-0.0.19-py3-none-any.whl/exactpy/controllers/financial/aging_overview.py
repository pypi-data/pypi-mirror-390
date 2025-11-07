from exactpy.controllers.base import BaseController
from exactpy.models.financial import AgingOverviewModel


class AgingOverviewController(BaseController):
    _resource = "read/financial/AgingOverview"
    _model = AgingOverviewModel


class AgingOverviewByAccountController(BaseController):
    _resource = "/read/financial/AgingOverviewByAccount"
    _model = AgingOverviewModel
