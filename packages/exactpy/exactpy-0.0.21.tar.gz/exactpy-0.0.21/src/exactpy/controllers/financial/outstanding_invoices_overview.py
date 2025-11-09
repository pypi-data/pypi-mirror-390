from exactpy.controllers.base import BaseController
from exactpy.models.financial import OutstandingInvoicesOverviewModel


class OustandingInvoicesOverviewController(BaseController):
    _resource = "read/financial/OutstandingInvoicesOverview"
    _model = OutstandingInvoicesOverviewModel
