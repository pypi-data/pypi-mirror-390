from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import (
    GUID,
    ExactUnixTimestamp,
    ReturnFrequencyEnum,
    ReturnStatusEnum,
    ReturnTypeEnum,
)


class ReturnModel(ExactOnlineBaseModel):
    document_id: GUID = SparkField(spark_type="string")
    amount: float | None = SparkField(spark_type="float", default=None)
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    currency: str | None = SparkField(spark_type="string", default=None)
    description: str | None = SparkField(spark_type="string", default=None)
    document_view_url: str | None = SparkField(spark_type="string", default=None)
    due_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    frequency: ReturnFrequencyEnum | None = SparkField(
        spark_type="string", default=None
    )
    payroll_declaration_type: str | None = SparkField(spark_type="string", default=None)
    period: int | None = SparkField(spark_type="integer", default=None)
    period_description: str | None = SparkField(spark_type="string", default=None)
    request: GUID = SparkField(spark_type="string")
    status: ReturnStatusEnum | None = SparkField(spark_type="integer", default=None)
    subject: str | None = SparkField(spark_type="string", default=None)
    type: ReturnTypeEnum | None = SparkField(spark_type="integer", default=None)
    year: int | None = SparkField(spark_type="integer", default=None)
