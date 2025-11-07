from exactpy.controllers.base import BaseController
from exactpy.models.financial import (
    ReportingBalanceModel,
)


class ReportingBalanceController(BaseController):
    _resource = "financial/ReportingBalance"
    _model = ReportingBalanceModel
