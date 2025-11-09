from exactpy.controllers.base import BaseController
from exactpy.models.financial import (
    RevenueListModel,
)
from exactpy.models.validation import YearAfterEntryQAModel, YearModel


class RevenueListController(BaseController):
    _resource = "read/financial/RevenueList"
    _model = RevenueListModel


class RevenueListByYearController(BaseController):
    _resource = "read/financial/RevenueListByYear"
    _query_args_model = YearModel
    _model = RevenueListModel


class RevenueListByYearAndStatusController(BaseController):
    _resource = "read/financial/RevenueListByYearAndStatus"
    _query_args_model = YearAfterEntryQAModel
    _model = RevenueListModel
