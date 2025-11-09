from exactpy.controllers.base import BaseController
from exactpy.models.crm import AccountModel


class AccountController(BaseController):
    _resource = "crm/Accounts"
    _model = AccountModel
