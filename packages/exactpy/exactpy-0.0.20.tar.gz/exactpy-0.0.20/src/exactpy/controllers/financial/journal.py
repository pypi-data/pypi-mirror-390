from exactpy.controllers.base import BaseController
from exactpy.models.financial import JournalModel


class JournalController(BaseController):
    _resource = "financial/Journals"
    _model = JournalModel
