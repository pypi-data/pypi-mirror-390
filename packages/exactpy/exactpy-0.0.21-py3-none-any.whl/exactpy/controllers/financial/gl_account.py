from exactpy.controllers.base import BaseController
from exactpy.models.financial import GLAccountModel


class GLAccountController(BaseController):
    _resource = "financial/GLAccounts"
    _model = GLAccountModel
    _expand = [
        "DeductibilityPercentages",
    ]
