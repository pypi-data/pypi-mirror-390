from typing import List

from sparkdantic import SparkField

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.models.crm.bank_account import BankAccountModel
from exactpy.types import GUID, ExactUnixTimestamp


class AccountModel(ExactOnlineBaseModel):
    id: GUID = SparkField(spark_type="string")
    accountant: GUID = SparkField(spark_type="string")
    account_manager: GUID = SparkField(spark_type="string")
    account_manager_full_name: str | None = SparkField(
        spark_type="string", default=None
    )
    account_manager_hid: int | None = SparkField(spark_type="integer", default=None)
    activity_sector: GUID = SparkField(spark_type="string")
    activity_sub_sector: GUID = SparkField(spark_type="string")
    address_line1: str | None = SparkField(spark_type="string", default=None)
    address_line2: str | None = SparkField(spark_type="string", default=None)
    address_line3: str | None = SparkField(spark_type="string", default=None)
    automatic_process_proposed_entry: int | None = SparkField(
        spark_type="integer", default=None
    )
    bank_accounts: List[BankAccountModel] = SparkField(exclude=True)
    blocked: bool = SparkField(spark_type="boolean", default=False)
    brin__: GUID = SparkField(spark_type="string")
    bsn__: str | None = SparkField(spark_type="string", default=None)
    business_type: GUID = SparkField(spark_type="string")
    can_drop_ship: bool = SparkField(spark_type="boolean", default=False)
    chamber_of_commerce: str | None = SparkField(spark_type="string", default=None)
    city: str | None = SparkField(spark_type="string", default=None)
    classification: GUID = SparkField(spark_type="string")
    classification1: GUID = SparkField(spark_type="string")
    classification2: GUID = SparkField(spark_type="string")
    classification3: GUID = SparkField(spark_type="string")
    classification4: GUID = SparkField(spark_type="string")
    classification5: GUID = SparkField(spark_type="string")
    classification6: GUID = SparkField(spark_type="string")
    classification7: GUID = SparkField(spark_type="string")
    classification8: GUID = SparkField(spark_type="string")
    classification_description: str | None = SparkField(
        spark_type="string", default=None
    )
    code: str | None = SparkField(spark_type="string", default=None)
    code_at_supplier: str | None = SparkField(spark_type="string", default=None)
    company_size: str | None = SparkField(spark_type="string", default=None)
    consolidation_scenario: int | None = SparkField(spark_type="integer", default=None)
    controlled_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    cost_center: str | None = SparkField(spark_type="string", default=None)
    cost_center_description: str | None = SparkField(spark_type="string", default=None)
    cost_paid: int | None = SparkField(spark_type="integer", default=None)
    country: str | None = SparkField(spark_type="string", default=None)
    country_name: str | None = SparkField(spark_type="string", default=None)
    created: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    creator: GUID = SparkField(spark_type="string")
    creator_full_name: str | None = SparkField(spark_type="string", default=None)
    credit_line_purchase: float | None = SparkField(spark_type="double", default=None)
    credit_line_sales: float | None = SparkField(spark_type="double", default=None)
    currency: str | None = SparkField(spark_type="string", default=None)
    customer_since: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    custom_field: str | None = SparkField(spark_type="string", default=None)
    datev_creditor_code: str | None = SparkField(spark_type="string", default=None)
    datev_debtor_code: str | None = SparkField(spark_type="string", default=None)
    delivery_advice: bytes | None = SparkField(spark_type="binary", default=None)
    discount_purchase: float | None = SparkField(spark_type="double", default=None)
    discount_sales: float | None = SparkField(spark_type="double", default=None)
    division: int | None = SparkField(spark_type="integer", default=None)
    document: GUID = SparkField(spark_type="string")
    duns_number: str | None = SparkField(spark_type="string", default=None)
    email: str | None = SparkField(spark_type="string", default=None)
    enable_sales_payment_link: bool | None = SparkField(
        spark_type="boolean", default=False
    )
    end_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    eori__number: str | None = SparkField(spark_type="string", default=None)
    established_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    fax: str | None = SparkField(spark_type="string", default=None)
    gl__account_purchase: GUID = SparkField(spark_type="string")
    gl__account_sales: GUID = SparkField(spark_type="string")
    glap__: GUID = SparkField(spark_type="string")
    glar__: GUID = SparkField(spark_type="string")
    gln_number: str | None = SparkField(spark_type="string", default=None)
    has_withholding_tax_sales: bool | None = SparkField(
        spark_type="boolean", default=False
    )
    ignore_datev_warning_message: bool = SparkField(spark_type="boolean", default=False)
    incoterm_address_purchase: str | None = SparkField(
        spark_type="string", default=None
    )
    incoterm_address_sales: str | None = SparkField(spark_type="string", default=None)
    incoterm_code_purchase: str | None = SparkField(spark_type="string", default=None)
    incoterm_code_sales: str | None = SparkField(spark_type="string", default=None)
    incoterm_version_purchase: int | None = SparkField(
        spark_type="integer", default=None
    )
    incoterm_version_sales: int | None = SparkField(spark_type="integer", default=None)
    intra_stat_area: str | None = SparkField(spark_type="string", default=None)
    intra_stat_delivery_term: str | None = SparkField(spark_type="string", default=None)
    intra_stat_system: str | None = SparkField(spark_type="string", default=None)
    intra_stat_transaction_a: str | None = SparkField(spark_type="string", default=None)
    intra_stat_transaction_b: str | None = SparkField(spark_type="string", default=None)
    intra_stat_transport_method: str | None = SparkField(
        spark_type="string", default=None
    )
    invoice_account: GUID = SparkField(spark_type="string")
    invoice_account_code: str | None = SparkField(spark_type="string", default=None)
    invoice_account_name: str | None = SparkField(spark_type="string", default=None)
    invoice_attachment_type: int | None = SparkField(spark_type="integer", default=None)
    invoicing_method: int | None = SparkField(spark_type="integer", default=None)
    is_accountant: int | None = SparkField(spark_type="integer", default=None)
    is_agency: int | None = SparkField(spark_type="integer", default=None)
    is_anonymised: int | None = SparkField(spark_type="integer", default=None)
    is_bank: bool = SparkField(spark_type="boolean", default=False)
    is_competitor: int | None = SparkField(spark_type="integer", default=None)
    is_extra_duty: bool | None = SparkField(spark_type="boolean", default=False)
    is_mailing: int | None = SparkField(spark_type="integer", default=None)
    is_member: bool = SparkField(spark_type="boolean", default=False)
    is_pilot: bool = SparkField(spark_type="boolean", default=False)
    is_purchase: bool = SparkField(spark_type="boolean", default=False)
    is_reseller: bool = SparkField(spark_type="boolean", default=False)
    is_sales: bool = SparkField(spark_type="boolean", default=False)
    is_supplier: bool = SparkField(spark_type="boolean", default=False)
    language: str | None = SparkField(spark_type="string", default=None)
    language_description: str | None = SparkField(spark_type="string", default=None)
    latitude: float | None = SparkField(spark_type="double", default=None)
    lead_purpose: GUID = SparkField(spark_type="string")
    lead_source: GUID = SparkField(spark_type="string")
    logo: bytes | None = SparkField(spark_type="binary", default=None)
    logo_file_name: str | None = SparkField(spark_type="string", default=None)
    logo_thumbnail_url: str | None = SparkField(spark_type="string", default=None)
    logo_url: str | None = SparkField(spark_type="string", default=None)
    longitude: float | None = SparkField(spark_type="double", default=None)
    main_contact: GUID = SparkField(spark_type="string")
    modified: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    modifier: GUID = SparkField(spark_type="string")
    modifier_full_name: str | None = SparkField(spark_type="string", default=None)
    name: str | None = SparkField(spark_type="string", default=None)
    oin__number: str | None = SparkField(spark_type="string", default=None)
    parent: GUID = SparkField(spark_type="string")
    pay_as_you_earn: str | None = SparkField(spark_type="string", default=None)
    payment_condition_purchase: str | None = SparkField(
        spark_type="string", default=None
    )
    payment_condition_purchase_description: str | None = SparkField(
        spark_type="string", default=None
    )
    payment_condition_sales: str | None = SparkField(spark_type="string", default=None)
    payment_condition_sales_description: str | None = SparkField(
        spark_type="string", default=None
    )
    peppol_identifier: str | None = SparkField(spark_type="string", default=None)
    peppol_identifier_type: int | None = SparkField(spark_type="integer", default=None)
    phone: str | None = SparkField(spark_type="string", default=None)
    phone_extension: str | None = SparkField(spark_type="string", default=None)
    postcode: str | None = SparkField(spark_type="string", default=None)
    price_list: GUID = SparkField(spark_type="string")
    purchase_currency: str | None = SparkField(spark_type="string", default=None)
    purchase_currency_description: str | None = SparkField(
        spark_type="string", default=None
    )
    purchase_lead_days: int | None = SparkField(spark_type="integer", default=None)
    purchase_vat_code: str | None = SparkField(spark_type="string", default=None)
    purchase_vat_code_description: str | None = SparkField(
        spark_type="string", default=None
    )
    recepient_of_commissions: bool = SparkField(spark_type="boolean", default=False)
    remarks: str | None = SparkField(spark_type="string", default=None)
    reseller: GUID = SparkField(spark_type="string")
    reseller_code: str | None = SparkField(spark_type="string", default=None)
    reseller_name: str | None = SparkField(spark_type="string", default=None)
    rsin__: str | None = SparkField(spark_type="string", default=None)
    sales_currency: str | None = SparkField(spark_type="string", default=None)
    sales_currency_description: str | None = SparkField(
        spark_type="string", default=None
    )
    sales_tax_schedule: GUID = SparkField(spark_type="string")
    sales_tax_schedule_code: str | None = SparkField(spark_type="string", default=None)
    sales_tax_schedule_description: str | None = SparkField(
        spark_type="string", default=None
    )
    sales_vat_code: str | None = SparkField(spark_type="string", default=None)
    sales_vat_code_description: str | None = SparkField(
        spark_type="string", default=None
    )
    search_code: str | None = SparkField(spark_type="string", default=None)
    security_level: int | None = SparkField(spark_type="integer", default=None)
    separate_inv_per_subscription: int | None = SparkField(
        spark_type="integer", default=None
    )
    shipping_lead_days: int | None = SparkField(spark_type="integer", default=None)
    shipping_method: GUID = SparkField(spark_type="string")
    show_remark_for_sales: bool | None = SparkField(spark_type="boolean", default=False)
    start_date: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    state: str | None = SparkField(spark_type="string", default=None)
    state_name: str | None = SparkField(spark_type="string", default=None)
    status: str | None = SparkField(spark_type="string", default=None)
    status_since: ExactUnixTimestamp = SparkField(spark_type="timestamp")
    trade_name: str | None = SparkField(spark_type="string", default=None)
    type: str | None = SparkField(spark_type="string", default=None)
    unique_taxpayer_reference: str | None = SparkField(
        spark_type="string", default=None
    )
    vat__liability: str | None = SparkField(spark_type="string", default=None)
    vat__number: str | None = SparkField(spark_type="string", default=None)
    website: str | None = SparkField(spark_type="string", default=None)
