from exactpy.controllers.base import BaseController
from exactpy.models.system import DivisionModel


class DivisionController(BaseController):
    _resource = "system/Divisions"
    _model = DivisionModel
