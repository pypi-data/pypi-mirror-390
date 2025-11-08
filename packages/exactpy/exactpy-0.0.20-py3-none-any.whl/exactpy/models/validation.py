from pydantic import AliasGenerator, BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from exactpy.types import GUID


class ExactOnlineQABaseModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(serialization_alias=to_camel),
        use_enum_values=True,
    )


class AccountQAModel(ExactOnlineQABaseModel):
    account_id: GUID


class AgeGroupQAModel(ExactOnlineQABaseModel):
    age_group: int


class AccountAgeGroupQAModel(ExactOnlineQABaseModel):
    account_id: GUID
    age_group: int


class GLSchemeReportingYearQAModel(ExactOnlineQABaseModel):
    gl_scheme: GUID
    reporting_year: int


class YearModel(ExactOnlineQABaseModel):
    year: int


class YearAfterEntryQAModel(ExactOnlineQABaseModel):
    year: int
    after_entry: bool
