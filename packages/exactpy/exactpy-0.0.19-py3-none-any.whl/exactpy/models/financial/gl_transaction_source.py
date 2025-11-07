from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel


class GLTransactionSourceModel(ExactOnlineBaseModel):
    id: int | None = SparkField(spark_type="integer", default=None)
    description: str | None = SparkField(spark_type="string", default=None)
    description_suffix: str | None = SparkField(spark_type="string", default=None)
