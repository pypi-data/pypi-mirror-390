from exactpy.controllers.base import BaseController
from exactpy.models.financial import (
    ReportingBalanceByClassificationModel,
)
from exactpy.models.validation import GLSchemeReportingYearQAModel


class ReportingBalanceByClassificationController(BaseController):
    _resource = "read/financial/ReportingBalanceByClassification"
    _query_args_model = GLSchemeReportingYearQAModel
    _model = ReportingBalanceByClassificationModel
