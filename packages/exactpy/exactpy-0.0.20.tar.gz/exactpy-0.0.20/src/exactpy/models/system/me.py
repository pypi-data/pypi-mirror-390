from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel


class MeModel(ExactOnlineBaseModel):
    user_id: str | None = SparkField(spark_type="string", default=None)
    accounting_division: int | None = SparkField(spark_type="integer", default=None)
    current_division: int | None = SparkField(spark_type="integer", default=None)
    customer_code: str | None = SparkField(spark_type="string", default=None)
    division_customer: str | None = SparkField(spark_type="string", default=None)
    division_customer_code: str | None = SparkField(spark_type="string", default=None)
    division_customer_name: str | None = SparkField(spark_type="string", default=None)
    division_customer_siret_number: str | None = SparkField(
        spark_type="string", default=None
    )
    division_customer_vat_number: str | None = SparkField(
        spark_type="string", default=None
    )
    dossier_division: int | None = SparkField(spark_type="integer", default=None)
    email: str | None = SparkField(spark_type="string", default=None)
    employee_id: str | None = SparkField(spark_type="string", default=None)
    first_name: str | None = SparkField(spark_type="string", default=None)
    full_name: str | None = SparkField(spark_type="string", default=None)
    gender: str | None = SparkField(spark_type="string", default=None)
    initials: str | None = SparkField(spark_type="string", default=None)
    is_client_use: bool = False
    is_employee_self_service_user: bool = False
    is_my_firm_lite_user: bool = False
    is_my_firm_portal_user: bool = False
    is_oei_migration_mandatory: bool = False
    is_starter_user: bool = False
    language: str | None = SparkField(spark_type="string", default=None)
    language_code: str | None = SparkField(spark_type="string", default=None)
    last_name: str | None = SparkField(spark_type="string", default=None)
    legislation: int | None = SparkField(spark_type="integer", default=None)
    middle_name: str | None = SparkField(spark_type="string", default=None)
    mobile: str | None = SparkField(spark_type="string", default=None)
    nationality: str | None = SparkField(spark_type="string", default=None)
    package_code: str | None = SparkField(spark_type="string", default=None)
    phone: str | None = SparkField(spark_type="string", default=None)
    phone_extension: str | None = SparkField(spark_type="string", default=None)
    picture_url: str | None = SparkField(spark_type="string", default=None)
    server_time: str | None = SparkField(spark_type="string", default=None)
    server_utc_offset: float | None = SparkField(spark_type="float", default=None)
    thumbnail_picture: bytes | None = SparkField(spark_type="binary", default=None)
    thumbnail_picture_format: str | None = SparkField(spark_type="string", default=None)
    title: str | None = SparkField(spark_type="string", default=None)
    user_name: str | None = SparkField(spark_type="string", default=None)
