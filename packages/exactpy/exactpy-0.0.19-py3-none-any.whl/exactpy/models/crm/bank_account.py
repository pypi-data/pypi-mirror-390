from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import GUID, BankAcountTypeEnum, ExactUnixTimestamp


class BankAccountModel(ExactOnlineBaseModel):
    id: GUID = SparkField(spark_type="string")
    account: GUID = SparkField(spark_type="string")
    account_name: str | None = SparkField(spark_type="string", default=None)
    bank: GUID = SparkField(spark_type="string")
    bank_account: str | None = SparkField(spark_type="string", default=None)
    bank_account_holder_name: str | None = SparkField(spark_type="string", default=None)
    bank_description: str | None = SparkField(spark_type="string", default=None)
    bank_name: str | None = SparkField(spark_type="string", default=None)
    bic__code: str | None = SparkField(spark_type="string", default=None)
    blocked: bool | None = SparkField(spark_type="string", default=None)
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    creator: GUID = SparkField(spark_type="string")
    creator_full_name: str | None = SparkField(spark_type="string", default=None)
    description: str | None = SparkField(spark_type="string", default=None)
    division: int | None = SparkField(spark_type="string", default=None)
    format: str | None = SparkField(spark_type="string", default=None)
    iban__: str | None = SparkField(spark_type="string", default=None)
    main: bool | None = SparkField(spark_type="string", default=None)
    modified: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    modifier: GUID = SparkField(spark_type="string")
    modifier_full_name: str | None = SparkField(spark_type="string", default=None)
    payment_service_account: GUID = SparkField(spark_type="string")
    type: BankAcountTypeEnum | None = SparkField(spark_type="string", default=None)
    type_description: str | None = SparkField(spark_type="string", default=None)
