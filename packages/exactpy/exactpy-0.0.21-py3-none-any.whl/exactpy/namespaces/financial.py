from __future__ import annotations

from typing import TYPE_CHECKING

from exactpy.controllers.financial import (
    AgingOverviewByAccountController,
    AgingOverviewController,
    AgingPayablesListByAgeGroupController,
    AgingPayablesListController,
    AgingReceivablesListByAgeGroupController,
    AgingReceivablesListController,
    DeductibilityPercentageController,
    ExchangeRateController,
    FinancialPeriodController,
    GLAccountClassificationMappingsController,
    GLAccountController,
    GLSchemeController,
    GLTransactionSourceController,
    GLTransactionTypeController,
    JournalController,
    JournalStatusListController,
    OfficialReturnController,
    OustandingInvoicesOverviewController,
    PayablesListByAccountAndAgeGroupController,
    PayablesListByAccountController,
    PayablesListByAgeGroupController,
    PayablesListController,
    ProfitLossOverviewController,
    ReceivablesListByAccountAndAgeGroupController,
    ReceivablesListByAccountController,
    ReceivablesListByAgeGroupController,
    ReceivablesListController,
    ReportingBalanceByClassificationController,
    ReportingBalanceController,
    ReturnController,
    RevenueListByYearAndStatusController,
    RevenueListByYearController,
    RevenueListController,
)
from exactpy.namespaces.base import Namespace

if TYPE_CHECKING:
    from exactpy.client import Client


class FinancialNamespace(Namespace):
    aging_overviews: AgingOverviewController
    aging_overviews_by_account: AgingOverviewByAccountController
    aging_payables_lists: AgingPayablesListController
    aging_payables_lists_by_age: AgingPayablesListByAgeGroupController
    aging_receivables_lists: AgingReceivablesListController
    aging_receivables_lists_by_age: AgingReceivablesListByAgeGroupController
    deductibilities: DeductibilityPercentageController
    exchange_rates: ExchangeRateController
    financial_periods: FinancialPeriodController
    gl_accounts_classification_mappings: GLAccountClassificationMappingsController
    gl_accounts: GLAccountController
    gl_schemes: GLSchemeController
    gl_transaction_sources: GLTransactionSourceController
    gl_transaction_types: GLTransactionTypeController
    journal_status_lists: JournalStatusListController
    journals: JournalController
    official_returns: OfficialReturnController
    outstanding_invoices_overviews: OustandingInvoicesOverviewController
    payables_lists: PayablesListController
    payables_lists_by_account: PayablesListByAccountController
    payables_lists_by_age_group: PayablesListByAgeGroupController
    payables_lists_by_account_and_age_group: PayablesListByAccountAndAgeGroupController
    receivables_lists: ReceivablesListController
    receivables_lists_by_account: ReceivablesListByAgeGroupController
    receivables_lists_by_age_group: ReceivablesListByAccountController
    receivables_lists_by_account_and_age_group: (
        ReceivablesListByAccountAndAgeGroupController
    )
    profit_loss_overviews: ProfitLossOverviewController
    reporting_balances: ReportingBalanceController
    reporting_balances_by_classification: ReportingBalanceByClassificationController
    returns: ReturnController
    revenue_lists: RevenueListController
    revenue_lists_by_year: RevenueListByYearController
    revenue_lists_by_year_and_status: RevenueListByYearAndStatusController

    def __init__(self, client: Client):
        super().__init__(client=client)

        self.aging_overviews = AgingOverviewController(self._client)
        self.aging_overviews_by_account = AgingOverviewByAccountController(self)
        self.aging_payables_lists = AgingPayablesListController(self._client)
        self.aging_payables_lists_by_age = AgingPayablesListByAgeGroupController(
            self._client
        )
        self.aging_receivables_lists = AgingReceivablesListController(self._client)
        self.aging_receivables_lists_by_age = AgingReceivablesListByAgeGroupController(
            self._client
        )
        self.deductibilities = DeductibilityPercentageController(self._client)
        self.exchange_rates = ExchangeRateController(self._client)
        self.financial_periods = FinancialPeriodController(self._client)
        self.gl_accounts_classification_mappings = (
            GLAccountClassificationMappingsController(self._client)
        )
        self.gl_accounts = GLAccountController(self._client)
        self.gl_schemes = GLSchemeController(self._client)
        self.gl_transaction_sources = GLTransactionSourceController(self._client)
        self.gl_transaction_types = GLTransactionTypeController(self._client)

        self.journal_status_lists = JournalStatusListController(self._client)
        self.journals = JournalController(self._client)
        self.official_returns = OfficialReturnController(self._client)
        self.outstanding_invoices_overviews = OustandingInvoicesOverviewController(
            self._client
        )
        self.payables_lists = PayablesListController(self._client)
        self.payables_lists_by_account = PayablesListByAccountController(self._client)
        self.payables_lists_by_age_group = PayablesListByAgeGroupController(self)
        self.payables_lists_by_account_and_age_group = (
            PayablesListByAccountAndAgeGroupController(self._client)
        )

        self.receivables_lists = ReceivablesListController(self._client)
        self.receivables_lists_by_account = ReceivablesListByAgeGroupController(
            self._client
        )
        self.receivables_lists_by_age_group = ReceivablesListByAccountController(
            self._client
        )
        self.receivables_lists_by_account_and_age_group = (
            ReceivablesListByAccountAndAgeGroupController(self._client)
        )
        self.profit_loss_overviews = ProfitLossOverviewController(self._client)
        self.reporting_balances = ReportingBalanceController(self._client)
        self.reporting_balances_by_classification = (
            ReportingBalanceByClassificationController(self._client)
        )
        self.returns = ReturnController(self._client)
        self.revenue_lists = RevenueListController(self._client)
        self.revenue_lists_by_year = RevenueListByYearController(self._client)
        self.revenue_lists_by_year_and_status = RevenueListByYearAndStatusController(
            self._client
        )
