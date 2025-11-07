from typing import Any, Dict, List, Type

import pytest
from pydantic import ValidationError

from exactpy.models.base import ExactOnlineBaseModel
from exactpy.utils import list_model_validate


class TestModel(ExactOnlineBaseModel):
    id: int
    name: str


@pytest.mark.parametrize(
    (
        "model",
        "raw_list",
        "skip_invalid",
        "expected_model_instances",
        "expected_validation_errors",
    ),
    [
        (
            TestModel,
            [{"ID": 1, "Name": "test"}, {"ID": 2}],
            True,
            [TestModel(**{"ID": 1, "Name": "test"})],
            [
                ValidationError(
                    "TestModel",
                    [],
                )
            ],
        ),
        (
            TestModel,
            [{"ID": 3, "Name": "another_test"}, {"ID": 4, "Name": "and_another_test"}],
            True,
            [
                TestModel(**{"ID": 3, "Name": "another_test"}),
                TestModel(**{"ID": 4, "Name": "and_another_test"}),
            ],
            [],
        ),
    ],
)
def test_list_model_validate(
    model: Type[ExactOnlineBaseModel],
    raw_list: List[Dict[str, Any]],
    skip_invalid: bool,
    expected_model_instances: List[Type[ExactOnlineBaseModel]],
    expected_validation_errors: List[ValidationError],
):
    model_instances, validation_errors = list_model_validate(
        model=model, raw_list=raw_list, skip_invalid=skip_invalid
    )
    assert len(expected_model_instances) == len(model_instances)
    assert expected_model_instances == model_instances
    assert len(expected_validation_errors) == len(validation_errors)


@pytest.mark.parametrize(
    (
        "model",
        "raw_list",
        "skip_invalid",
        "expected_exception_type",
    ),
    [
        (
            TestModel,
            [{"ID": 1, "Name": "test"}, {"ID": 2}],
            False,
            ValidationError,
        )
    ],
)
def test_list_model_validate_raises(
    model: Type[ExactOnlineBaseModel],
    raw_list: List[Dict[str, Any]],
    skip_invalid: bool,
    expected_exception_type: ValidationError,
):
    with pytest.raises(expected_exception=expected_exception_type):
        list_model_validate(model=model, raw_list=raw_list, skip_invalid=skip_invalid)
