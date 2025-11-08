from exactpy.controllers.base import BaseController
from exactpy.models.financial import GLTransactionSourceModel


class GLTransactionSourceController(BaseController):
    _resource = "financial/GLSchemes"
    _model = GLTransactionSourceModel
