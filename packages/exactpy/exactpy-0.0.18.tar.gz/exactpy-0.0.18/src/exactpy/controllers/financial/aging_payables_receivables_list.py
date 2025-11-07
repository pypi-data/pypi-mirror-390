from exactpy.controllers.base import BaseController
from exactpy.models.financial import AgingPayablesReceivablesListModel
from exactpy.models.validation import AgeGroupQAModel


class AgingPayablesListController(BaseController):
    _resource = "read/financial/AgingPayablesList"
    _model = AgingPayablesReceivablesListModel


class AgingReceivablesListController(BaseController):
    _resource = "read/financial/AgingReceivablesList"
    _model = AgingPayablesReceivablesListModel


class AgingPayablesListByAgeGroupController(BaseController):
    _resource = "read/financial/AgingPayablesListByAgeGroup"
    _query_args_model = AgeGroupQAModel
    _model = AgingPayablesReceivablesListModel
    _expand = []


class AgingReceivablesListByAgeGroupController(BaseController):
    _resource = "read/financial/AgingReceivablesListByAgeGroup"
    _query_args_model = AgeGroupQAModel
    _model = AgingPayablesReceivablesListModel
