from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import GUID, ExactUnixTimestamp


class DeductibilityPercentageModel(ExactOnlineBaseModel):
    id: GUID = SparkField(spark_type="string")
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    creator: GUID = SparkField(spark_type="string")
    creator_full_name: str | None = SparkField(spark_type="string", default=None)
    division: int | None = SparkField(spark_type="integer", default=None)
    end_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    expense_non_deductible_percentage: float | None = SparkField(
        spark_type="double", default=None
    )
    gl__account: GUID = SparkField(spark_type="string")
    line_number: int | None = SparkField(spark_type="integer", default=None)
    modified: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    modifier: GUID = SparkField(spark_type="string")
    modifier_full_name: str | None = SparkField(spark_type="string", default=None)
    private_use_percentage: float | None = SparkField(spark_type="double", default=None)
    start_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    vat__non_deductible_percentage: float | None = SparkField(
        spark_type="double", default=None
    )
