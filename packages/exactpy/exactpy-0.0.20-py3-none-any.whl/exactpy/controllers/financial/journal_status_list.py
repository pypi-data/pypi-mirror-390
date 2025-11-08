from exactpy.controllers.base import BaseController
from exactpy.models.financial import JournalStatusListModel


class JournalStatusListController(BaseController):
    _resource = "read/financial/JournalStatusList"
    _model = JournalStatusListModel
