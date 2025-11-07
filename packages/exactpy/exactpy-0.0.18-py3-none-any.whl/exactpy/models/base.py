from pydantic import AliasGenerator, ConfigDict
from sparkdantic import SparkModel

from exactpy.alias_generators import special_snake_to_pascal

TYPE_MAPPING = {}


class ExactOnlineBaseModel(SparkModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(alias=special_snake_to_pascal),
        validate_by_alias=True,
        use_enum_values=True,
    )

    # Indicates what field is used as primary key
    _pk: str | None
