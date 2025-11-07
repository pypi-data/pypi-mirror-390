from exactpy.controllers.base import BaseController
from exactpy.models.financial import DeductibilityPercentageModel


class DeductibilityPercentageController(BaseController):
    _resource = "financial/DeductibilityPercentages"
    _model = DeductibilityPercentageModel
