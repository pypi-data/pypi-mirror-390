from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import (
    GUID,
)


class AgingPayablesReceivablesListModel(ExactOnlineBaseModel):
    _pk = "account_id"
    account_id: GUID = SparkField(spark_type="string")
    account_code: str | None = SparkField(spark_type="string", default=None)
    account_name: str | None = SparkField(spark_type="string", default=None)
    age_group1: int | None = SparkField(spark_type="integer", default=None)
    age_group1_amount: int | None = SparkField(spark_type="double", default=None)
    age_group1_description: str | None = SparkField(spark_type="string", default=None)
    age_group2: int | None = SparkField(spark_type="integer", default=None)
    age_group2_amount: int | None = SparkField(spark_type="double", default=None)
    age_group2_description: str | None = SparkField(spark_type="string", default=None)
    age_group3: int | None = SparkField(spark_type="integer", default=None)
    age_group3_amount: int | None = SparkField(spark_type="double", default=None)
    age_group3_description: str | None = SparkField(spark_type="string", default=None)
    age_group4: int | None = SparkField(spark_type="integer", default=None)
    age_group4_amount: float | None = SparkField(spark_type="double", default=None)
    age_group4_description: str | None = SparkField(spark_type="string", default=None)
    currency_code: str | None = SparkField(spark_type="string", default=None)
    total_amount: float | None = SparkField(spark_type="double", default=None)
