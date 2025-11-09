from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import GUID, ExactUnixTimestamp


class GLSchemeModel(ExactOnlineBaseModel):
    _pk = "id"
    id: GUID = SparkField(spark_type="string")
    code: str | None = SparkField(spark_type="string", default=None)
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    creator: GUID = SparkField(spark_type="string")
    creator_full_name: str | None = SparkField(spark_type="string", default=None)
    description: str | None = SparkField(spark_type="string", default=None)
    division: int | None = SparkField(spark_type="integer", default=None)
    main: int | None = SparkField(spark_type="integer", default=None)
    modified: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    modifier: GUID = SparkField(spark_type="string")
    modifier_full_name: str | None = SparkField(spark_type="string", default=None)
    target_namespace: str | None = SparkField(spark_type="string", default=None)
