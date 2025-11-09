from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import (
    GUID,
    ExactUnixTimestamp,
    JournalFrequencyEnum,
    ReturnSourceEnum,
)


class OfficialReturnModel(ExactOnlineBaseModel):
    _pk = "id"
    id: GUID = SparkField(spark_type="string")
    amount: float | None = SparkField(spark_type="double", default=None)
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    creator: GUID = SparkField(spark_type="string")
    creator_full_name: str | None = SparkField(spark_type="string", default=None)
    description: str | None = SparkField(spark_type="string", default=None)
    division: int | None = SparkField(spark_type="integer", default=None)
    document: GUID = SparkField(spark_type="string")
    document_subject: str | None = SparkField(spark_type="string", default=None)
    frequency: JournalFrequencyEnum | None = SparkField(
        spark_type="integer", default=None
    )
    is_correction: int | None = SparkField(spark_type="integer", default=None)
    modified: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    modifier: GUID = SparkField(spark_type="string")
    modifier_full_name: str | None = SparkField(spark_type="string", default=None)
    period: int | None = SparkField(spark_type="integer", default=None)
    presentation_data: str | None = SparkField(spark_type="string", default=None)
    presentation_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    presentation_file: bytes | None = SparkField(spark_type="binary", default=None)
    presentation_file_name: str | None = SparkField(spark_type="string", default=None)
    reference: str | None = SparkField(spark_type="string", default=None)
    source: ReturnSourceEnum | None = SparkField(spark_type="integer", default=None)
    status: int | None = SparkField(spark_type="integer", default=None)
    type: int | None = SparkField(spark_type="integer", default=None)
    type_description: str | None = SparkField(spark_type="string", default=None)
    year: int | None = SparkField(spark_type="integer", default=None)
