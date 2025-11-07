from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel


class ProfitLossOverviewModel(ExactOnlineBaseModel):
    _pk = "current_year"
    current_year: int
    costs_current_period: float | None = SparkField(spark_type="float", default=None)
    costs_current_year: float | None = SparkField(spark_type="float", default=None)
    costs_previous_year: float | None = SparkField(spark_type="float", default=None)
    costs_previous_year_period: float | None = SparkField(
        spark_type="float", default=None
    )
    currency_code: str | None = SparkField(spark_type="string", default=None)
    current_period: int | None = SparkField(spark_type="integer", default=None)
    previous_year: int | None = SparkField(spark_type="integer", default=None)
    previous_year_period: int | None = SparkField(spark_type="integer", default=None)
    result_current_period: float | None = SparkField(spark_type="float", default=None)
    result_current_year: float | None = SparkField(spark_type="float", default=None)
    result_previous_year: float | None = SparkField(spark_type="float", default=None)
    result_previous_year_period: float | None = SparkField(
        spark_type="float", default=None
    )
    revenue_current_period: float | None = SparkField(spark_type="float", default=None)
    revenue_current_year: float | None = SparkField(spark_type="float", default=None)
    revenue_previous_year: float | None = SparkField(spark_type="float", default=None)
    revenue_previous_year_period: float | None = SparkField(
        spark_type="float", default=None
    )
