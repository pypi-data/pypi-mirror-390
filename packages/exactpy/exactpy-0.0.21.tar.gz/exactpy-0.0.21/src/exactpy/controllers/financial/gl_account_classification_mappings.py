from exactpy.controllers.base import BaseController
from exactpy.models.financial import (
    GLAccountClassificationMappingsModel,
)


class GLAccountClassificationMappingsController(BaseController):
    _resource = "financial/GLAccountClassificationMappings"
    _model = GLAccountClassificationMappingsModel
