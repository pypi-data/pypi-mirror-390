from typing import Literal, Type, overload
from ..schemas.common import (
    StandardOrganizationSchema,
    FullOrganizationSchema,
    AnyOrganizationSchemaType,
)
from ..enums.organization import Granularity


@overload
def get_schema_model(
    granularity: Literal[Granularity.STANDARD],
    /,
) -> Type[StandardOrganizationSchema]: ...
@overload
def get_schema_model(
    granularity: Literal[Granularity.FULL],
    /,
) -> Type[FullOrganizationSchema]: ...
@overload
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnyOrganizationSchemaType: ...
def get_schema_model(
    granularity: Granularity = Granularity.STANDARD,
    /,
) -> AnyOrganizationSchemaType:
    if granularity is Granularity.STANDARD:
        return StandardOrganizationSchema
    elif granularity is Granularity.FULL:
        return FullOrganizationSchema
