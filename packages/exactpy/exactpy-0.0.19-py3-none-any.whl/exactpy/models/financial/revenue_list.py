from exactpy.models.base import ExactOnlineBaseModel


class RevenueListModel(ExactOnlineBaseModel):
    period: int
    year: int
    amount: float
