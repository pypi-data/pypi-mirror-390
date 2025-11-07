from exactpy.controllers.base import BaseController
from exactpy.models.financial import PayablesReceivablesListModel
from exactpy.models.validation import (
    AccountAgeGroupQAModel,
    AccountQAModel,
    AgeGroupQAModel,
)


class PayablesListController(BaseController):
    _resource = "read/financial/PayablesList"
    _model = PayablesReceivablesListModel


class ReceivablesListController(BaseController):
    _resource = "read/financial/ReceivablesList"
    _model = PayablesReceivablesListModel


class PayablesListByAgeGroupController(BaseController):
    _resource = "read/financial/PayablesListByAgeGroup"
    _query_args_model = AgeGroupQAModel
    _model = PayablesReceivablesListModel


class ReceivablesListByAgeGroupController(BaseController):
    _resource = "read/financial/ReceivablesListByAgeGroup"
    _query_args_model = AgeGroupQAModel
    _model = PayablesReceivablesListModel
    _expand = []


class PayablesListByAccountController(BaseController):
    _resource = "read/financial/PayablesListByAccount"
    _query_args_model = AccountQAModel
    _model = PayablesReceivablesListModel
    _expand = []


class ReceivablesListByAccountController(BaseController):
    _resource = "read/financial/ReceivablesListByAccount"
    _query_args_model = AccountQAModel
    _model = PayablesReceivablesListModel


class PayablesListByAccountAndAgeGroupController(BaseController):
    _resource = "read/financial/PayablesListByAccountAndAgeGroup"
    _query_args_model = AccountAgeGroupQAModel
    _model = PayablesReceivablesListModel


class ReceivablesListByAccountAndAgeGroupController(BaseController):
    _resource = "read/financial/ReceivablesListByAccountAndAgeGroup"
    _query_args_model = AccountAgeGroupQAModel
    _model = PayablesReceivablesListModel
