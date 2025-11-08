from exactpy.controllers.base import BaseController
from exactpy.models.financial import GLSchemeModel


class GLSchemeController(BaseController):
    _resource = "financial/GLSchemes"
    _model = GLSchemeModel
