from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel


class OutstandingInvoicesOverviewModel(ExactOnlineBaseModel):
    _pk = "currency_code"
    currency_code: str | None = SparkField(spark_type="string", default=None)
    outstanding_payable_invoice_amount: float | None = SparkField(
        spark_type="float", default=None
    )
    outstanding_payable_invoice_count: float | None = SparkField(
        spark_type="float", default=None
    )
    outstanding_receivable_invoice_amount: float | None = SparkField(
        spark_type="float", default=None
    )
    outstanding_receivable_invoice_count: float | None = SparkField(
        spark_type="float", default=None
    )
    overdue_payable_invoice_amount: float | None = SparkField(
        spark_type="float", default=None
    )
    overdue_payable_invoice_count: float | None = SparkField(
        spark_type="float", default=None
    )
    overdue_receivable_invoice_amount: float | None = SparkField(
        spark_type="float", default=None
    )
    overdue_receivable_invoice_count: float | None = SparkField(
        spark_type="float", default=None
    )
