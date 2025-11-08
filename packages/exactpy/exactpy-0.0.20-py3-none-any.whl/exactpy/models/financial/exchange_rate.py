from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import GUID, ExactUnixTimestamp


class ExchangeRateModel(ExactOnlineBaseModel):
    _pk = "id"
    id: GUID = SparkField(spark_type="string")
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    creator: GUID = SparkField(spark_type="string")
    creator_full_name: str | None = SparkField(spark_type="string", default=None)
    division: int | None = SparkField(spark_type="integer", default=None)
    modified: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    modifier: GUID = SparkField(spark_type="string")
    modifier_full_name: str | None = SparkField(spark_type="string", default=None)
    rate: float | None = SparkField(spark_type="double", default=None)
    source_currency: str | None = SparkField(spark_type="string", default=None)
    source_currency_description: str | None = SparkField(
        spark_type="string", default=None
    )
    start_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    target_currency: str | None = SparkField(spark_type="string", default=None)
    target_currency_description: str | None = SparkField(
        spark_type="string", default=None
    )
