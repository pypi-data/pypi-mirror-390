from datetime import datetime
from enum import IntEnum, StrEnum
from typing import Annotated

from pydantic import BeforeValidator, PlainSerializer

from exactpy.serializers import exact_unix_transformer
from exactpy.validators import exact_unix_validator, guid_validator

ExactUnixTimestamp = Annotated[
    datetime | None,
    BeforeValidator(exact_unix_validator),
    PlainSerializer(exact_unix_transformer),
]

GUID = Annotated[str | None, BeforeValidator(guid_validator), "guid"]


class BalanceTypeEnum(StrEnum):
    BALANCE_SHEET = "B"
    PROFIT_AND_LOSS = "W"


class BalanceSideEnum(StrEnum):
    CREDIT = "C"
    DEBIT = "D"


class CostCenterEnum(IntEnum):
    OPTIONAL = 0
    MANDATORY = 1
    NO = 2


class CostUnitEnum(IntEnum):
    OPTIONAL = 0
    MANDATORY = 1
    NO = 2


class VATSystemEnum(StrEnum):
    INVOICE = "I"
    CASH = "C"


class BankAcountTypeEnum(StrEnum):
    ACCOUNT = "a"
    EMPLOYEE = "e"
    CASH = "k"
    PAYMENT_SERVICE = "p"
    BANK = "r"
    STUDENT = "s"
    UNKNOWN = "u"


class GLAccountTypeEnum(IntEnum):
    CASH = 10
    BANK = 12
    CREDIT_CARD = 14
    PAYMENT_SERVICES = 16
    ACCOUNTS_RECEIVABLE = 20
    PREPAYMENT_ACCOUNTS_RECEIVABLE = 21
    ACCOUNTS_PAYABLE = 22
    VAT = 24
    EMPLOYEES_PAYABLE = 25
    PREPAID_EXPENSES = 26
    ACCRUED_EXPENSES = 27
    INCOME_TAXES_PAYABLE = 29
    FIXED_ASSETS = 30
    OTHER_ASSETS = 32
    ACCUMULATED_DEPRECIATION = 35
    INVENTORY = 40
    CAPITAL_STOCK = 50
    RETAINED_EARNINGS = 52
    LONG_TERM_DEBT = 55
    CURRENT_PORTION_OF_DEBT = 60
    GENERAL = 90
    TAX_PAYABLE = 100
    REVENUE = 110
    COST_OF_GOODS = 111
    OTHER_COSTS = 120
    SALES_GENERAL_ADMINISTRATIVE_EXPENSES = 121
    DEPRECIATION_COSTS = 122
    RESEARCH_AND_DEVELOPMENT = 123
    EMPLOYEE_COSTS = 125
    EMPLOYMENT_COST = 126
    EXCEPTIONAL_COSTS = 130
    EXCEPTIONAL_INCOME = 140
    INCOME_TAXES = 150
    INTEREST_INCOME = 160
    YEAR_END_REFLECTION = 300
    INDIRECT_YEAR_END_COSTING = 301
    DIRECT_YEAR_END_COSTING = 302


class PaymentServiceProviderTypeEnum(IntEnum):
    ADYEN: 1
    PAYPAL: 2
    STRIPE: 3


class JournalTypeEnum(IntEnum):
    CASH: 10
    BANK: 12
    PAYMENT_SERVICE: 16
    SALES: 20
    RETURN_INVOICE: 21
    PURCHASE: 22
    RECEIVED_RETURN_INVOICE: 23
    GENERAL_JOURNAL: 90


class JournalStatusEnum(IntEnum):
    OPEN = 0
    CLOSED = 1


class ReturnSourceEnum(IntEnum):
    EOL: 1
    REST_API: 2


class JournalFrequencyEnum(IntEnum):
    MONTHLY: 10
    TWO_MONTHLY: 20
    QUARTERLY: 30
    YEARLY: 40
    FINANCIAL_YEAR_QUARTER: 100


class ApprovalStatusEnum(IntEnum):
    NA = 1
    AWAITING_REVIEW = 2
    AWAITING_APPROVAL = 3
    APPROVED = 4


class ReportingBalanceStatusEnum(IntEnum):
    OPEN = 20
    PROCESSED = 50


class ReturnFrequencyEnum(StrEnum):
    MONTHLY = "m"
    QUARTERLY = "q"
    FINANCIAL_YEAR_QUARTER = "a"
    YEARLY = "y"


class ReturnStatusEnum(IntEnum):
    NULL = -10
    VOID = 0
    REJECTED = 5
    DRAFT = 10
    OPEN = 20
    APPROVED = 30
    REALIZED = 40
    PROCESSED = 50


class ReturnTypeEnum(IntEnum):
    VAT: 31
    EC_SALES_LIST: 32
    PAYROLL_DECLARATION: 146


class BlockingStatusEnum(IntEnum):
    NOT_BLOCKED = 0
    BACKUP_RESTORE = 1
    CONVERSION__BUSY = 2
    CONVERSION_SHADOW = 3
    CONVERSION_WAITING = 4
    COPY_DATA_WAITING = 5
    COPY_DATA_BUSY = 6


class DivisionStatusEnum(IntEnum):
    INACTIVE = 0
    ACTIVE = 1
    ARCHIVED = 2
