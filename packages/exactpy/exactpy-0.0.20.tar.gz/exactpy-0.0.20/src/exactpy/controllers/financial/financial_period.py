from exactpy.controllers.base import BaseController
from exactpy.models.financial import FinancialPeriodModel


class FinancialPeriodController(BaseController):
    _resource = "financial/FinancialPeriods"
    _model = FinancialPeriodModel
