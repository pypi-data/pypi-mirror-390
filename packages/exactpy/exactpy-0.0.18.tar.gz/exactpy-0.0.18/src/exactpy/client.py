import time
from datetime import datetime
from enum import StrEnum
from pathlib import Path
from typing import Callable, Dict, List, Type
from urllib.parse import parse_qs, urlparse

import httpx
from loguru import logger

from exactpy.auth import Auth
from exactpy.controllers.crm import (
    AccountController,
)
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
from exactpy.controllers.system import (
    DivisionController,
    MeController,
)
from exactpy.exceptions import DailyLimitExceededException, NoDivisionSetException

BASE_HEADERS = {"Content-Type": "application/json", "Accept": "application/json"}


class FilterOperatorEnum(StrEnum):
    AND = "and"
    OR = "or"


class Namespace: ...


class Client:
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_url: str,
        caching_enabled: bool = True,
        write_cache_callable: Callable | None = Auth.write_cache,
        write_cache_callable_kwargs: dict = {"cache_path": Path("./creds.json")},
        read_cache_callable: Callable | None = Auth.read_cache,
        read_cache_callable_kwargs: dict = {"cache_path": Path("./creds.json")},
        base_url: str = "https://start.exactonline.nl/api",
        auth_url: str | None = None,
        token_url: str | None = None,
        endpoints_url: str | None = None,
        current_division: int | None = None,
        verbose: bool = True,
    ):
        """An Exact Online Python client.

        Args:
            client_id (str): The Exact Online app registration client ID.
            client_secret (str): The Exact Online app registration client secret.
            caching_enabled (bool): Whether cache callables should be called automatically. Defaults to True.
            cache_callable (Callable | None, optional): Callable to use for caching token info.
                Defaults to None. If set tot None, caching as well as cache loading will be
                disabled.
            cache_callable_kwargs (dict, optional): Keyword arguments to use for cache_callable.
                Defaults to {}.
            read_cache_callable (Callable | None, optional): Callable to use for loading cached token info.
                Defaults to None. If caching was disabled, loading cache won't happen either.
            read_cache_callable_kwargs (dict, optional): Keyword arguments to use for read_cache_callable.
                Defaults to {}.
            redirect_url (str): The redirect url, needs to match exactly what
                was entered in the app registration in the Exact Online portal.
            base_url (str, optional): The API base url. Defaults to "https://start.exactonline.nl/api".
            auth_url (str | None, optional): The auth base url. Defaults to None. If unset (None), it will be derived from base_url.
            token_url (str | None, optional): _description_. Defaults to None. If unset (None), it will be derived from base_url.
            endpoints_url (str | None, optional): the v1 endpoints url. Defaults to None. If unset (None), it will be derived from base_url
            current_division (int, optional): The current division to use. Defaults to None.
            verbose (bool, optional): _description_. Defaults to True.
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.verbose = verbose

        self.current_division = current_division

        self.base_url = base_url.rstrip("/")
        if not self.base_url.endswith("api"):
            raise ValueError("base_url does not end in api, cannot proceed.")

        if endpoints_url is None:
            self.endpoints_url = f"{self.base_url}/v1"
            if verbose:
                logger.info(
                    f"endpoints_url was not set. Derived from base_url: {self.endpoints_url}"
                )
        self.endpoints_url = self.endpoints_url.rstrip("/")

        if token_url is None:
            token_url = f"{self.base_url}/oauth2/token"
            if verbose:
                logger.info(
                    f"access_token_url was not set. Derived from base_url: {token_url}"
                )
        token_url = token_url.rstrip("/")

        if auth_url is None:
            auth_url = f"{self.base_url}/oauth2/auth"
            if verbose:
                logger.info(f"auth_url was not set. Derived from base_url: {auth_url}")
        auth_url = auth_url.rstrip("/")

        self.auth_client = Auth(
            client_id=client_id,
            client_secret=client_secret,
            auth_url=auth_url,
            token_url=token_url,
            redirect_url=redirect_url,
            caching_enabled=caching_enabled,
            write_cache_callable=write_cache_callable,
            write_cache_callable_kwargs=write_cache_callable_kwargs,
            read_cache_callable=read_cache_callable,
            read_cache_callable_kwargs=read_cache_callable_kwargs,
            verbose=self.verbose,
        )

        self._rate_limits_max_daily_calls = -1
        self._rate_limits_remaining_daily_calls = -1
        self._rate_limits_daily_reset = -1.0
        self._rate_limits_max_minutely_calls = -1
        self._rate_limits_remaining_minutely_calls = -1
        self._rate_limits_minutely_reset = -1.0

        self._setup_namespaces_and_controllers()

    @staticmethod
    def _parse_query_args(query_args: Dict[str, str]) -> str:
        """Build string of query args key, value pairs.

        Args:
            query_args (Dict[str, str]): The query args key value pairs.

        Returns:
            str: The query arg string.
        """
        parsed_query_args = []
        for key, val in query_args.items():
            parsed_query_args.append(f"{key}={val}")

        return "&".join(parsed_query_args)

    @staticmethod
    def _parse_filters(
        filters: Dict[str, str], filter_operator: Type[FilterOperatorEnum]
    ) -> str:
        """Build url filter string from filter dict.

        Args:
            filters (Dict[str, str]): The filter key value pairs.

        Returns:
            str: Filters in Exact Online string form.
        """
        parsed_filters = []
        op = str(filter_operator)
        for key, val in filters.items():
            # We only want quotes for strings, not for bools and numerics
            qu = (
                ""
                if (isinstance(val, str) and val.lower() in ("true", "false"))
                or isinstance(val, int)
                else "'"
            )
            pref = ("", f" {op} ")[len(parsed_filters) > 0]
            parsed_filters.append(f"{pref}{key} eq {qu}{val}{qu}")

        return ",".join(parsed_filters)

    @staticmethod
    def _get_skip_token(next_url: str) -> str:
        """Get skip token from next url.

        Args:
            next_url(str): API response next url containing skip token.

        Returns:
            str: the complete skip token query param key value pair in string form.
        """
        parsed_url = urlparse(next_url)
        return parse_qs(parsed_url.query)["$skiptoken"][0]

    def _check_division(self):
        if self.current_division is None:
            raise NoDivisionSetException(
                "You must set a division. You can pass this on init (current_division arg) or set it using client.division = client.get_current_division_id()."
            )

    def set_initial_division(self):
        """When no calls have been made, there is no current division yet.
        This method retrieves the current division from the api and sets it
        as the current division in the client."""
        self.current_division = self.get_current_division_id()

    def get_current_division_id(self):
        """Retrieve current division id from the api"""
        return self.system.me.show().current_division

    def get_current_division(self):
        return self.system.divisions.show(primary_key_value=self.current_division)

    def _update_rate_limits(self, headers: httpx.Headers):
        """Updates usages and rate limits for current client
        as given by Exact Online rest api response headers.

        Args:
            headers (httpx.Headers): The httpx call response headers.
        """
        if "x-ratelimit-limit" not in headers:
            return

        self._rate_limits_max_daily_calls = int(headers["x-ratelimit-limit"])
        self._rate_limits_remaining_daily_calls = int(headers["x-ratelimit-remaining"])
        self._rate_limits_daily_reset = float(headers["x-ratelimit-reset"]) / 1000
        self._rate_limits_max_minutely_calls = int(
            headers["x-ratelimit-minutely-limit"]
        )
        self._rate_limits_remaining_minutely_calls = int(
            headers["x-ratelimit-minutely-remaining"]
        )
        self._rate_limits_minutely_reset = (
            float(headers["x-ratelimit-minutely-reset"]) / 1000
        )

    def _check_rate_limits(self):
        if self._rate_limits_remaining_minutely_calls == 0:
            if self.verbose:
                exp = datetime.fromtimestamp(self._rate_limits_minutely_reset)
                logger.warning(
                    f"No remaining minutely calls. Waiting until {exp.strftime('%H:%m')} to continue."
                )
            time.sleep(self._rate_limits_minutely_reset - time.time())

        if self._rate_limits_remaining_daily_calls == 0:
            raise DailyLimitExceededException(
                "Daily limit has been exceeded and the default behavior is to error out. Try again later."
            )

    def count(self, resource: str, include_division: bool = True) -> int:
        """This method uses the odata `$count` query option to
        retrieve a count of all records. No filters can be used.

        Args:
            resource (str): The Exact Online API url resource to use.
            include_division (bool): Whether to include the current division in the url. Defaults to True.

        Returns:
            int: The number of available records on the server.
        """
        if include_division:
            self._check_division()
        division_part = ("", f"/{self.current_division}")[include_division]

        self._check_rate_limits()

        headers = self.auth_client._check_token_and_get_headers()
        headers.update(BASE_HEADERS)

        # Delete accept header because it isn't needed
        # for the count api call
        # See also:
        # https://support.exactonline.com/community/s/knowledge-base#All-All-DNO-Simulation-query-string-options
        del headers["Accept"]

        url = f"{self.endpoints_url}{division_part}/{resource}/$count"

        req = httpx.get(url=url, headers=headers)
        self._update_rate_limits(req.headers)
        if req.status_code != 200:
            logger.error(f"Request failed with status code {req.status_code} Content:")
            print(req.content)
            req.raise_for_status()
        return req

    def get(
        self,
        resource: str,
        query_args: Dict[str, str] = {},
        filters: Dict[str, str] = {},
        filter_operator: Type[FilterOperatorEnum] = FilterOperatorEnum.AND,
        select: List[str] = [],
        expand: List[str] = [],
        top: int | None = None,
        inline_count: bool = False,
        include_division: bool = True,
        skip_token: str | None = None,
    ) -> httpx.Response:
        """Calls a get endpoint.

        Args:
            resource (str): The Exact Online API url resource to use.
            query_args (Dict[str, str]): A dictionary of
                query arg name and value key pairs to send to the endpoint. Defaults to {}.
            filters (Dict[str, str]): A dictionary of
                filter name and filter value key pairs to send to the endpoint. Defaults to {}.
            filter_operator (Type[FilterOperatorEnum]): Operator to use to join the filters (and/or).
            select (List[str]): Attributes to select. Defaults to [].
            expand (List[str]): Attributes to expand. Defaults to [].
            top (int, Optional): The number of records (from start) to retrieve.
                Defaults to None, meaning all records.
            inline_count (bool): Whether to include the inlinecount query arg; this will add
                a `__count` property to the response body with a count of all records.
                Note that if top is set, inline count isn't available and this argument will
                do nothing.
            include_division (bool): Whether to include the current division in the url. Defaults to True.
            skip_token: (str, Optional): A skiptoken query arg, used for paging in the Exact Online
                rest api. Defaults to None.

        Returns:
            httpx.Response: the API call httpx response object.
        """
        if include_division:
            self._check_division()
        division_part = ("", f"/{self.current_division}")[include_division]

        self._check_rate_limits()

        headers = self.auth_client._check_token_and_get_headers()
        headers.update(BASE_HEADERS)

        parsed_query_args = Client._parse_query_args(query_args=query_args)

        parsed_filters = Client._parse_filters(
            filters=filters, filter_operator=filter_operator
        )
        parsed_select = ",".join(select)
        parsed_expand = ",".join(expand)

        url = f"{self.endpoints_url}{division_part}/{resource}"

        existing_qargs = len(query_args) > 0
        url += ("", f"?{parsed_query_args}")[existing_qargs]

        join_str = ("?", "&")[existing_qargs]
        url += ("", f"{join_str}$filter={parsed_filters}")[len(filters) > 0]

        existing_qargs = existing_qargs | len(filters) > 0
        join_str = ("?", "&")[existing_qargs]
        url += ("", f"{join_str}$select={parsed_select}")[len(select) > 0]

        existing_qargs = existing_qargs | len(select) > 0
        join_str = ("?", "&")[existing_qargs]
        url += ("", f"{join_str}$expand={parsed_expand}")[len(expand) > 0]

        existing_qargs = existing_qargs | len(expand) > 0
        join_str = ("?", "&")[existing_qargs]
        url += ("", f"{join_str}$skiptoken={skip_token}")[skip_token is not None]

        existing_qargs = existing_qargs | (skip_token is not None)
        join_str = ("?", "&")[existing_qargs]
        url += ("", f"{join_str}$top={top}")[top is not None]

        existing_qargs = existing_qargs | (top is not None)
        join_str = ("?", "&")[existing_qargs]
        url += ("", f"{join_str}$inlinecount=allpages")[inline_count]

        req = httpx.get(url=url, headers=headers)

        self._update_rate_limits(req.headers)
        if req.status_code != 200:
            logger.error(f"Request failed with status code {req.status_code} Content:")
            print(req.content)
            req.raise_for_status()
        return req

    def show(
        self,
        resource: str,
        primary_key_value: str,
        primary_key: str = "ID",
        select: List[str] = [],
        expand: List[str] = [],
        include_division: bool = True,
        is_guid: bool = True,
    ) -> httpx.Response:
        """Calls a get endpoint

        Args:
            filters (Dict[str, str]): A dictionary of
                filter name and filter value key pairs to send to the endpoint.
            primary_key_value (str): Value of the primary key field
            primary_key (str): Name of the primary field. Defaults to "ID".
            select (List[str]): Attributes to select. Defaults to [].
            expand (List[str]): Attributes to expand. Defaults to [].
            include_division (bool): Whether to include the current division in the url. Defaults to True.

        Returns:
            httpx.Response: the API call httpx response object.
        """
        if include_division:
            self._check_division()

        self._check_rate_limits()

        headers = self.auth_client._check_token_and_get_headers()
        headers.update(BASE_HEADERS)
        parsed_select = ",".join(select)
        parsed_expand = ",".join(expand)

        division_part = ("", f"/{self.current_division}")[include_division]
        url = f"{self.endpoints_url}{division_part}/{resource}"
        if is_guid:
            url += f"?$filter={primary_key} eq guid '{primary_key_value}'"
        else:
            url += f"?$filter={primary_key} eq {primary_key_value}"
        url += ("", f"&$select={parsed_select}")[len(select) > 0]
        url += ("", f"&$expand={parsed_expand}")[len(expand) > 0]

        req = httpx.get(url=url, headers=headers)
        self._update_rate_limits(req.headers)
        if req.status_code != 200:
            logger.error(f"Request failed with status code {req.status_code} Content:")
            print(req.content)
            req.raise_for_status()
        return req

    def _setup_namespaces_and_controllers(self):
        """Register namespaces and initialize controller classes."""
        # Set up namespaces
        self.financial = Namespace()
        self.crm = Namespace()
        self.system = Namespace()

        # Set up endpoints
        self.financial.aging_overviews = AgingOverviewController(self)
        self.financial.aging_overviews_by_account = AgingOverviewByAccountController(
            self
        )
        self.financial.aging_payables_lists = AgingPayablesListController(self)
        self.financial.aging_payables_lists_by_age = (
            AgingPayablesListByAgeGroupController(self)
        )
        self.financial.aging_receivables_lists = AgingReceivablesListController(self)
        self.financial.aging_receivables_lists_by_age = (
            AgingReceivablesListByAgeGroupController(self)
        )
        self.financial.deductibilities = DeductibilityPercentageController(self)
        self.financial.exchange_rates = ExchangeRateController(self)
        self.financial.financial_periods = FinancialPeriodController(self)
        self.financial.gl_accounts_classification_mappings = (
            GLAccountClassificationMappingsController(self)
        )
        self.financial.gl_accounts = GLAccountController(self)
        self.financial.gl_schemes = GLSchemeController(self)
        self.financial.gl_transaction_sources = GLTransactionSourceController(self)
        self.financial.gl_transaction_types = GLTransactionTypeController(self)

        self.financial.journal_status_lists = JournalStatusListController(self)
        self.financial.journals = JournalController(self)
        self.financial.official_returns = OfficialReturnController(self)
        self.financial.outstanding_invoices_overviews = (
            OustandingInvoicesOverviewController(self)
        )
        self.financial.payables_lists = PayablesListController(self)
        self.financial.payables_lists_by_account = PayablesListByAccountController(self)
        self.financial.payables_lists_by_age_group = PayablesListByAgeGroupController(
            self
        )
        self.financial.payables_lists_by_account_and_age_group = (
            PayablesListByAccountAndAgeGroupController(self)
        )

        self.financial.receivables_lists = ReceivablesListController(self)
        self.financial.receivables_lists_by_account = (
            ReceivablesListByAgeGroupController(self)
        )
        self.financial.receivables_lists_by_age_group = (
            ReceivablesListByAccountController(self)
        )
        self.financial.receivables_lists_by_account_and_age_group = (
            ReceivablesListByAccountAndAgeGroupController(self)
        )
        self.financial.profit_loss_overviews = ProfitLossOverviewController(self)
        self.financial.reporting_balances = ReportingBalanceController(self)
        self.financial.reporting_balances_by_classification = (
            ReportingBalanceByClassificationController(self)
        )
        self.financial.returns = ReturnController(self)
        self.financial.revenue_lists = RevenueListController(self)
        self.financial.revenue_lists_by_year = RevenueListByYearController(self)
        self.financial.revenue_lists_by_year_and_status = (
            RevenueListByYearAndStatusController(self)
        )

        self.crm.accounts = AccountController(self)
        self.system.me = MeController(self)
        self.system.divisions = DivisionController(self)
