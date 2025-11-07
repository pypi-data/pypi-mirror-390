from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import (
    GUID,
    ExactUnixTimestamp,
    GLAccountTypeEnum,
    JournalTypeEnum,
    PaymentServiceProviderTypeEnum,
)


class JournalModel(ExactOnlineBaseModel):
    id: GUID = SparkField(spark_type="string")
    allow_variable_currency: bool | None = None
    allow_variable_exchange_rate: bool | None = None
    allow_vat__: bool | None = None
    auto_save: bool | None = None
    bank: GUID = SparkField(spark_type="string")
    bank_account_bic_code: str | None = SparkField(spark_type="string", default=None)
    bank_account_country: str | None = SparkField(spark_type="string", default=None)
    bank_account_description: str | None = SparkField(spark_type="string", default=None)
    bank_account_iban: str | None = SparkField(spark_type="string", default=None)
    bank_account_id: GUID = SparkField(spark_type="string")
    bank_account_including_mask: str | None = SparkField(
        spark_type="string", default=None
    )
    bank_account_use_sepa: bool | None = None
    bank_account_use_sepa_direct_debit: bool | None = None
    bank_name: str | None = SparkField(spark_type="string", default=None)
    code: str | None = SparkField(spark_type="string", default=None)
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    creator: GUID = SparkField(spark_type="string")
    creator_full_name: str | None = SparkField(spark_type="string", default=None)
    currency: str | None = SparkField(spark_type="string", default=None)
    currency_description: str | None = SparkField(spark_type="string", default=None)
    custom_field: str | None = SparkField(spark_type="string", default=None)
    description: str | None = SparkField(spark_type="string", default=None)
    division: int | None = SparkField(spark_type="integer", default=None)
    gl__account: GUID = SparkField(spark_type="string")
    gl__account_code: str | None = SparkField(spark_type="string", default=None)
    gl__account_description: str | None = SparkField(spark_type="string", default=None)
    gl__account_type: GLAccountTypeEnum | None = SparkField(
        spark_type="integer", default=None
    )
    is_blocked: bool | None = None
    modified: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    modifier: GUID = SparkField(spark_type="string")
    modifier_full_name: str | None = SparkField(spark_type="string", default=None)
    payment_in_transit_account: GUID = SparkField(spark_type="string")
    payment_service_account_identifier: str | None = SparkField(
        spark_type="string", default=None
    )
    payment_service_provider: PaymentServiceProviderTypeEnum = SparkField(
        spark_type="integer"
    )
    payment_service_provider_name: str | None = SparkField(
        spark_type="string", default=None
    )
    type: JournalTypeEnum | None = SparkField(spark_type="integer", default=None)
