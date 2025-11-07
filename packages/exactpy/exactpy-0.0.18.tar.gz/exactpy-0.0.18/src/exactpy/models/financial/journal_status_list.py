from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import (
    JournalStatusEnum,
    JournalTypeEnum,
)


class JournalStatusListModel(ExactOnlineBaseModel):
    journal: str | None = SparkField(spark_type="string", default=None)
    period: int | None = SparkField(spark_type="integer", default=None)
    year: int | None = SparkField(spark_type="integer", default=None)
    journal_description: str | None = SparkField(spark_type="string", default=None)
    journal_type: JournalTypeEnum | None = SparkField(
        spark_type="integer", default=None
    )
    journal_type_description: str | None = SparkField(spark_type="string", default=None)
    status: JournalStatusEnum | None = SparkField(spark_type="integer", default=None)
    status_description: str | None = SparkField(spark_type="string", default=None)
