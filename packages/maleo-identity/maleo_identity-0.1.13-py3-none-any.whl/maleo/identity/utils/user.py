from typing import Literal, Type, overload
from ..schemas.common import (
    StandardUserSchema,
    FullUserSchema,
    AnyUserSchemaType,
)
from ..enums.user import Granularity


@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardUserSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullUserSchema]: ...
@overload
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnyUserSchemaType: ...
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnyUserSchemaType:
    if granularity is Granularity.STANDARD:
        return StandardUserSchema
    elif granularity is Granularity.FULL:
        return FullUserSchema
