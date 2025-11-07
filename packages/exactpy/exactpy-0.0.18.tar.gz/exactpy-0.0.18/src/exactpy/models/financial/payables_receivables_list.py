from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.types import (
    GUID,
    ApprovalStatusEnum,
    ExactUnixTimestamp,
)


class PayablesReceivablesListModel(ExactOnlineBaseModel):
    _pk = "hid__"
    hid__: int
    account_code: str | None = SparkField(spark_type="string", default=None)
    account_id: GUID = SparkField(spark_type="string")
    account_name: str | None = SparkField(spark_type="string", default=None)
    amount: float | None = SparkField(spark_type="float", default=None)
    amount_in_transit: float | None = SparkField(spark_type="float", default=None)
    approval_status: ApprovalStatusEnum | None = SparkField(
        spark_type="integer", default=None
    )
    currency_code: str | None = SparkField(spark_type="string", default=None)
    description: str | None = SparkField(spark_type="string", default=None)
    due_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    entry_number: int | None = SparkField(spark_type="integer", default=None)
    id: GUID | None
    invoice_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    invoice_number: int | None = SparkField(spark_type="integer", default=None)
    journal_code: str | None = SparkField(spark_type="string", default=None)
    journal_description: str | None = SparkField(spark_type="string", default=None)
    # todo
    # notes: List[Node]
    your_ref: str | None = SparkField(spark_type="string", default=None)
