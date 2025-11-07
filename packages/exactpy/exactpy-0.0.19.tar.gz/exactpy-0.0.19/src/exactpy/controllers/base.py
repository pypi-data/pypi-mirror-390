from __future__ import annotations

import typing
from typing import (
    TYPE_CHECKING,
    Annotated,
    Dict,
    Generator,
    List,
    Tuple,
    Type,
    Union,
    get_origin,
)

from loguru import logger
from pydantic import BaseModel

from exactpy.exceptions import NoFiltersSetException
from exactpy.models.base import ExactOnlineBaseModel
from exactpy.utils import create_partial_model, list_model_validate

if TYPE_CHECKING:
    from exactpy.client import Client


class BaseController:
    _resource: str
    _query_args_model: Type[BaseModel] | None = None
    _mandatory_filter_options: List[str] = []
    _model: Type[BaseModel]
    _expand: List[str] = []

    def __init__(
        self,
        client: Client,
    ):
        self._client = client

    def _check_query_args(
        self, query_args: Dict[str, Union[str, int, float]] = {}
    ) -> dict:
        """Validates query args using a pydantic model, and returns a dict
        dumped by the pydantic validation model if successful.

        Args:
            query_args (Dict[str, Union[str, int, float]], optional):
                Dict of query arg key, value pairs. Defaults to {}

        Raises:
            ValidationError: Raised if query args don't pass pydantic model validation.

        Returns:
            dict: The query arg pydantic model dump.
        """
        if self._query_args_model is None:
            return {}

        # Dump query args to dict in (Exact Online) aliases
        query_args = self._query_args_model.model_validate(query_args).model_dump()
        query_args_by_alias = self._query_args_model.model_validate(
            query_args
        ).model_dump(by_alias=True)
        # We have to modify GUID args so that its value matches guid '<val>'
        # print(self._query_args_model.model_fields)
        for key, val in query_args.items():
            if self._is_guid(key, model=self._query_args_model):
                query_args_by_alias[
                    self._query_args_model.model_fields[key].serialization_alias
                ] = f"guid'{val}'"
        # print(query_args_by_alias)
        return query_args_by_alias

    def _check_filters(self, filters: Dict[str, Union[str, int, float]] = {}):
        """Checks whether (the right) filters have been set in case
        they are mandatory.

        Args:
            filters (Dict[str, Union[str, int, float]], optional):  Dict of filter key, value pairs. Defaults to {}

        Raises:
            NoFiltersSetException: Raised when no filters are set while there are mandatory filters.
        """
        filter_options = ", ".join(self._mandatory_filter_options)
        if len(self._mandatory_filter_options) > 0 and len(filters) == 0:
            raise NoFiltersSetException(
                f"This model requires a mandatory filter. Choices are '{filter_options}'"
            )
        elif (
            len(self._mandatory_filter_options) > 0
            and set(self._mandatory_filter_options).intersection(filters.keys()) == {}
        ):
            raise NoFiltersSetException(
                f"No valid mandatory filter set. Choices are '{filter_options}'"
            )

        # Convert filter names to Exact Online naming (Pascal case)
        parsed_filters = {
            self._model.model_fields[field].alias: value
            for field, value in filters.items()
            if field in self._model.model_fields
        }

        return parsed_filters

    def fields_to_aliases(self, fields: List[str]) -> List[str]:
        """Convert list of field names into aliases.

        Args:
            fields (List[str]): List of model field names.

        Returns:
            List[str]: List of model field aliases.
        """
        return [self._model.model_fields[field].alias for field in fields]

    def _is_guid(self, key: str, model: Type[BaseModel]):
        is_guid = False
        pk_type = typing.get_type_hints(model, include_extras=True)[key]
        if get_origin(pk_type) is Annotated:
            is_guid = pk_type.__metadata__[-1] == "guid"
        return is_guid

    def show(
        self,
        primary_key_value: Union[str, int],
        expand: List[str] = [],
    ) -> Type[ExactOnlineBaseModel]:
        """Retrieve a single instance of a model by primary key.

        Args:
            primary_key_value (Union[str, int]): value of primary key field.
            expand (List[str], optional): Attributes to expand (in Exact Online naming, so
                Pascal case). Defaults to [].

        Returns:
            Type[ExactOnlineBaseModel]: In instance of a subclass of ExactOnlineBaseModel.
        """

        if self._model._pk is None:
            raise ValueError("Model's primary key (_pk) property is not set.")

        # Set expand attributes if they aren't set
        if expand == []:
            expand = self._expand

        is_guid = self._is_guid(self._model._pk.default, self._model)

        # Retrieve single instance and convert to pydantic
        return self._model.model_validate(
            self._client.show(
                resource=self._resource,
                primary_key=self._model.model_fields[self._model._pk.default].alias,
                primary_key_value=primary_key_value,
                expand=expand,
                is_guid=is_guid,
            ).json()["d"]["results"][0],
            extra="ignore",
        )

    def all_paged(
        self,
        query_args: Dict[str, str] = {},
        filters: Dict[str, Union[str, int, float]] = {},
        select: List[str] = [],
        expand: List[str] = [],
        top: int | None = None,
        inline_count: bool = False,
        max_pages: int = -1,
        skip_invalid: bool = True,
    ) -> Generator[
        List[Type[ExactOnlineBaseModel]] | Tuple[List[Type[ExactOnlineBaseModel]], int],
        None,
        None,
    ]:
        """Retrieve a collection of model instances using given
        filters.

        Args:
            query_args (Dict[str, str]): A dictionary of
                query arg name and value key pairs to send to the endpoint. Defaults to {}.
            filters (Dict[str, Union[str, int, float]], optional):  Dict of filter key,
                value pairs. Defaults to {}
            select (List[str], optional): Attributes to select (in Exact Online naming,
                so Pascal case). Defaults to [].
            expand (List[str], optional): Attributes to expand (in Exact Online naming,
                so Pascal case). Defaults to [].
            top (int, Optional): The number of records (from start) to retrieve.
                Defaults to None, meaning all records.
            inline_count (bool): Whether to include the inlinecount query arg; this will add
                a `__count` property to the response body with a count of all records.
                Note that if top is set, inline count isn't available and this argument will
                do nothing.
            max_pages (int, optional): Max number of pages to retrieve. Defaults to -1 (no limit).
                Note that `max_pages` will have no effect when top is set, because there is no
                paging on the API side in that case.
            skip_invalid (bool): Whether to not throw a validation error when encountering
                an invalid input, but just skip it.
        Returns:
            Generator[List[Type[ExactOnlineBaseModel]] | Tuple[List[Type[ExactOnlineBaseModel]], None, None]:
                A page level generator that produces lists of instances of a subclass of ExactOnlineBaseModel.
                Depending on whether or not inline_count is set to True, the generator return type is either a
                list of model instances or a tuple of a list of model instances and integer that represents the
                number of records.
        """
        if max_pages == 0:
            return []

        page_count = 0

        # Check mandatory filters and query args
        parsed_filters = self._check_filters(filters=filters)
        query_arg_dump = self._check_query_args(query_args=query_args)

        # Set expand attributes if they aren't set
        if expand == []:
            expand = self._expand

        # Check if select cols are set. If so, we have to
        # generate a partial model with those fields.
        model = self._model
        if len(select) > 0:
            model = create_partial_model(
                model=self._model,
                fields=select,
            )

        # Parse select cols into Exact Online naming (Pascal case)
        parsed_select = self.fields_to_aliases(fields=select)

        if self._client.verbose:
            logger.info(f"Fetching page {page_count + 1}")

        # Initial get request to get first page
        resp = self._client.get(
            resource=self._resource,
            query_args=query_arg_dump,
            filters=parsed_filters,
            select=parsed_select,
            expand=expand,
            top=top,
            inline_count=inline_count,
        ).json()

        # If top is set, results are not in the sub key
        # result, but just in the level above that (`d`).
        raw_results = resp["d"]
        if top is None:
            raw_results = raw_results["results"]

        # Convert to Pydantic
        results, validation_errors = list_model_validate(
            model=model, raw_list=raw_results, skip_invalid=skip_invalid
        )

        if self._client.verbose:
            if len(validation_errors) > 0:
                logger.error(
                    "Some input was not validated correctly and those instances were skipped."
                )
            for val_error in validation_errors:
                logger.error(str(val_error))

        if inline_count and top is None:
            count = resp["d"]["__count"]
            yield results, count
        else:
            yield results

        # We need to quit early when top is set,
        # because `d` will a list and will have no property `__next`
        if top is not None:
            return

        while (next_url := resp["d"].get("__next")) is not None:
            page_count += 1
            if max_pages != -1 and page_count + 1 > max_pages:
                break

            if self._client.verbose:
                logger.info(f"Fetching page {page_count + 1}")

            # Extract the skip token, in order to obtain the next page
            skip_token = self._client._get_skip_token(next_url)

            # Get page
            resp = self._client.get(
                resource=self._resource,
                query_args=query_arg_dump,
                filters=parsed_filters,
                select=parsed_select,
                expand=expand,
                top=top,
                inline_count=inline_count,
                skip_token=skip_token,
            ).json()

            # If top is set, results are not in the sub key
            # result, but just in the level above that (`d`).
            raw_results = resp["d"]
            if top is None:
                raw_results = raw_results["results"]

            # Convert to Pydantic
            temp_results, validation_errors = list_model_validate(
                model=model,
                raw_list=raw_results,
                skip_invalid=skip_invalid,
            )

            if self._client.verbose:
                if len(validation_errors) > 0:
                    logger.error(
                        "Some input was not validated correctly and those instances were skipped."
                    )
                for val_error in validation_errors:
                    logger.error(str(val_error))

            if inline_count and top is None:
                count = resp["d"]["__count"]
                yield temp_results, count
            else:
                yield temp_results

        if self._client.verbose:
            logger.info(f"Fetched a total of {len(results)} records.")

    def count(self) -> int:
        """Uses the `odata` $count query arg to get a count
        of all records. No filters can be used.

        Returns:
            int: The count of all records
        """
        return int(self._client.count(resource=self._resource).content)

    def all(
        self,
        query_args: Dict[str, str] = {},
        filters: Dict[str, Union[str, int, float]] = {},
        select: List[str] = [],
        expand: List[str] = [],
        top: int | None = None,
        inline_count: bool = False,
        max_pages: int = -1,
        skip_invalid: bool = True,
    ) -> (
        List[Type[ExactOnlineBaseModel]] | Tuple[List[Type[ExactOnlineBaseModel]], int]
    ):
        """This is a convenience method, that just collects all pages
        for all_paged into a single list. This might be convenient
        in some cases where there aren't that many results or where
        memory isn't an issue.

        Args:
            query_args (Dict[str, str]): A dictionary of
                query arg name and value key pairs to send to the endpoint. Defaults to {}.
            filters (Dict[str, Union[str, int, float]], optional):  Dict of filter key,
                value pairs. Defaults to {}
            select (List[str], optional): Attributes to select (in Exact Online naming,
                so Pascal case). Defaults to [].
            expand (List[str], optional): Attributes to expand (in Exact Online naming,
                so Pascal case). Defaults to [].
            top (int, Optional): The number of records (from start) to retrieve.
                Defaults to None, meaning all records.
            inline_count (bool): Whether to include the inlinecount query arg; this will add
                a `__count` property to the response body with a count of all records.
                Note that if top is set, inline count isn't available and this argument will
                do nothing.
            max_pages (int, optional): Max number of pages to retrieve. Defaults to -1 (no limit).
                Note that `max_pages` will have no effect when top is set, because there is no
                paging on the API side in that case.
            skip_invalid (bool): Whether to not throw a validation error when encountering
                an invalid input, but just skip it.
        Returns:
            List[Type[ExactOnlineBaseModel]] | Tuple[List[Type[ExactOnlineBaseModel]], int]:
                Either returns a list of instances of a subclass of ExactOnlineBaseMode or, if inline_count
                is set to True, a tuple of the aforementioned list and the count of all records.
        """
        results = []
        record_count = 0

        if inline_count and top is None:
            for page, count in self.all_paged(
                query_args=query_args,
                filters=filters,
                select=select,
                expand=expand,
                top=top,
                inline_count=True,
                max_pages=max_pages,
                skip_invalid=skip_invalid,
            ):
                results += page
                record_count = count
            return results, record_count
        else:
            for page in self.all_paged(
                query_args=query_args,
                filters=filters,
                select=select,
                expand=expand,
                top=top,
                inline_count=False,
                max_pages=max_pages,
                skip_invalid=skip_invalid,
            ):
                results += page
            return results
