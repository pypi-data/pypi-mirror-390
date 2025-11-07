from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import GUID


class GLAccountClassificationMappingsModel(ExactOnlineBaseModel):
    id: GUID = SparkField(spark_type="string")
    classification: GUID = SparkField(spark_type="string")
    classification_code: str | None = SparkField(spark_type="string", default=None)
    classification_description: str | None = SparkField(
        spark_type="string", default=None
    )
    division: int | None = SparkField(spark_type="integer", default=None)
    gl__account: GUID = SparkField(spark_type="string")
    gl__account_code: str | None = SparkField(spark_type="string", default=None)
    gl__account_description: str | None = SparkField(spark_type="string", default=None)
    gl__scheme_code: str | None = SparkField(spark_type="string", default=None)
    gl__scheme_description: str | None = SparkField(spark_type="string", default=None)
    gl__scheme_id__: GUID = SparkField(spark_type="string")
