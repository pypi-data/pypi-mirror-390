from typing import Any, Dict, List, Tuple, Type

from loguru import logger
from pydantic import TypeAdapter, ValidationError, create_model

from exactpy.models.base import ExactOnlineBaseModel


def create_partial_model(
    model: Type[ExactOnlineBaseModel], fields: List[str]
) -> Type[ExactOnlineBaseModel]:
    """
    Create a new ExactOnlineBaseModel subclass with only the specified fields.

    Args:
        model (Type[ExactOnlineBaseModel]): The original ExactOnlineBaseModel subclass.
        fields (List[str]): List of field names to include in the new model.

    Returns:
        A new ExactOnlineBaseModel subclass with only the specified fields.
    """
    model_fields = model.model_fields
    partial_fields = {
        field: (model_fields[field].annotation, model_fields[field].default)
        for field in fields
        if field in model_fields
    }

    partial_model = create_model(
        f"{model.__name__}__partial", __base__=model, **partial_fields
    )

    return partial_model


def list_model_validate(
    model: Type[ExactOnlineBaseModel],
    raw_list: List[Dict[str, Any]],
    skip_invalid: bool = True,
    verbose: bool = False,
) -> Tuple[List[Type[ExactOnlineBaseModel]], List[ValidationError]]:
    """Attempts to validate a list of python objects using given Pydantic model.

    Args:
        model (Type[ExactOnlineBaseModel]): The model to use for validation and
            to use as output model.
        raw_list (List[Dict[str, Any]]): The list of to be validated input dicts.
        skip_invalid (bool): Whether to skip dicts in the input that didn't validate.
            If set to True, a list of validation errors will be given as second
            element in the output tuple. This will loop over the input list and
            manually attempt to validate each single model.
            If set to False, a regular TypeAdapter[List[...]] will be used and an exception
            will be raised as soon as a model fails to validate. Defaults to True.
        skip_invalid (bool): Whether to be verbose with logging. Defaults to False.

    Returns:
        Tuple[List[Type[ExactOnlineBaseModel]], List[ValidationError]]: A tuple of
            a list of pydantic models and a list of of ValidationErrors for dicts
            that didn't validate.
    """

    if not skip_invalid:
        if verbose:
            logger.info("Using regular TypeAdapter[List[...]] for validation.")
        list_adapter = TypeAdapter(List[model])
        return (list_adapter.validate_python(raw_list), [])

    if verbose:
        logger.info("Using loop to perform individual model validation.")
    model_instances = []
    validation_errors = []
    for raw_list_item in raw_list:
        try:
            model_instances.append(model.model_validate(raw_list_item))
        except ValidationError as e:
            validation_errors.append(e)

    return (model_instances, validation_errors)
