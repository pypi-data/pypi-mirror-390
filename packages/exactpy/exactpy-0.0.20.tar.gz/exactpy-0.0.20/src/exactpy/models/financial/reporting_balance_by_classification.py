from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import GUID, BalanceTypeEnum, ReportingBalanceStatusEnum


class ReportingBalanceByClassificationModel(ExactOnlineBaseModel):
    id: int
    amount: float | None = SparkField(spark_type="float", default=None)
    amount_credit: float | None = SparkField(spark_type="float", default=None)
    amount_debit: float | None = SparkField(spark_type="float", default=None)
    balance_type: BalanceTypeEnum | None = SparkField(spark_type="string", default=None)
    classification_code: str | None = SparkField(spark_type="string", default=None)
    classification_description: str | None = SparkField(
        spark_type="string", default=None
    )
    cost_center_code: str | None = SparkField(spark_type="string", default=None)
    cost_center_description: str | None = SparkField(spark_type="string", default=None)
    cost_unit_code: str | None = SparkField(spark_type="string", default=None)
    cost_unit_description: str | None = SparkField(spark_type="string", default=None)
    count: int | None = SparkField(spark_type="integer", default=None)
    division: int | None = SparkField(spark_type="integer", default=None)
    gl__account: GUID = SparkField(spark_type="string")
    gl__account_code: str | None = SparkField(spark_type="string", default=None)
    gl__account_description: str | None = SparkField(spark_type="string", default=None)
    gl__scheme: GUID = SparkField(spark_type="string")
    reporting_period: int | None = SparkField(spark_type="integer", default=None)
    reporting_year: int | None = SparkField(spark_type="integer", default=None)
    status: ReportingBalanceStatusEnum | None = SparkField(
        spark_type="integer", default=None
    )
    type: int | None = SparkField(spark_type="integer", default=None)
