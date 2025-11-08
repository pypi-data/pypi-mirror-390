from exactpy.controllers.base import BaseController
from exactpy.models.financial import GLTransactionTypeModel


class GLTransactionTypeController(BaseController):
    _resource = "financial/GLSchemes"
    _model = GLTransactionTypeModel
