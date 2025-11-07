from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel


class AgingOverviewModel(ExactOnlineBaseModel):
    _pk = "age_group"
    age_group: int | None = SparkField(spark_type="integer", default=None)
    age_group_description: str | None = SparkField(spark_type="string", default=None)
    amount_payable: float | None = SparkField(spark_type="double", default=None)
    amount_receivable: float | None = SparkField(spark_type="double", default=None)
    currency_code: str | None = SparkField(spark_type="string", default=None)
