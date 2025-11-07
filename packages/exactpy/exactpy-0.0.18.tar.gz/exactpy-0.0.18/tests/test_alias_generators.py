import pytest

from exactpy.alias_generators import special_snake_to_pascal


@pytest.mark.parametrize(
    ("snake", "expected_pascal"),
    [
        ("this__is_pascal_case", "THISIsPascalCase"),
        ("this_is_gnu__linux", "ThisIsGNULinux"),
        ("gl__account_purchase", "GLAccountPurchase"),
        ("id", "ID"),
        ("id__", "ID"),
    ],
)
def test_special_snake_to_pascal(snake: str, expected_pascal: str):
    assert special_snake_to_pascal(snake) == expected_pascal
