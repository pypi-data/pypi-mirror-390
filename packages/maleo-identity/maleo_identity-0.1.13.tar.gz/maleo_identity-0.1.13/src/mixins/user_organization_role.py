from pydantic import Field
from typing import Annotated, Literal, TypeGuard
from uuid import UUID
from maleo.schemas.mixins.identity import Identifier
from maleo.types.any import ManyAny
from maleo.types.string import ManyStrs
from ..enums.user_organization_role import IdentifierType
from ..types.user_organization_role import CompositeIdentifier, IdentifierValueType


class UserOrganizationRoleIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def columns_and_values(self) -> tuple[ManyStrs, ManyAny]:
        values = self.value if isinstance(self.value, tuple) else (self.value,)
        return self.type.columns, values


class IdUserOrganizationRoleIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDUserOrganizationRoleIdentifier(
    Identifier[Literal[IdentifierType.UUID], UUID]
):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class CompositeUserOrganizationRoleIdentifier(
    Identifier[Literal[IdentifierType.COMPOSITE], CompositeIdentifier]
):
    type: Annotated[
        Literal[IdentifierType.COMPOSITE],
        Field(IdentifierType.COMPOSITE, description="Identifier's type"),
    ] = IdentifierType.COMPOSITE
    value: Annotated[CompositeIdentifier, Field(..., description="Identifier's value")]


AnyUserOrganizationRoleIdentifier = (
    UserOrganizationRoleIdentifier
    | IdUserOrganizationRoleIdentifier
    | UUIDUserOrganizationRoleIdentifier
    | CompositeUserOrganizationRoleIdentifier
)


def is_id_identifier(
    identifier: AnyUserOrganizationRoleIdentifier,
) -> TypeGuard[IdUserOrganizationRoleIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyUserOrganizationRoleIdentifier,
) -> TypeGuard[UUIDUserOrganizationRoleIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_composite_identifier(
    identifier: AnyUserOrganizationRoleIdentifier,
) -> TypeGuard[CompositeUserOrganizationRoleIdentifier]:
    return identifier.type is IdentifierType.COMPOSITE and isinstance(
        identifier.value, tuple
    )
