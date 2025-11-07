from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from maleo.schemas.mixins.identity import Identifier
from maleo.types.any import ManyAny
from maleo.types.boolean import OptBoolT
from maleo.types.misc import OptListOfAnyOrStrToAnyDict
from maleo.types.string import ManyStrs
from ..enums.organization_relation import IdentifierType
from ..types.organization_relation import CompositeIdentifier, IdentifierValueType


class IsBidirectional(BaseModel, Generic[OptBoolT]):
    is_bidirectional: Annotated[OptBoolT, Field(..., description="Is Bidirectional")]


class Meta(BaseModel):
    meta: Annotated[OptListOfAnyOrStrToAnyDict, Field(None, description="Meta")] = None


class OrganizationRelationIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def columns_and_values(self) -> tuple[ManyStrs, ManyAny]:
        values = self.value if isinstance(self.value, tuple) else (self.value,)
        return self.type.columns, values


class IdOrganizationRelationIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDOrganizationRelationIdentifier(
    Identifier[Literal[IdentifierType.UUID], UUID]
):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class CompositeOrganizationRelationIdentifier(
    Identifier[Literal[IdentifierType.COMPOSITE], CompositeIdentifier]
):
    type: Annotated[
        Literal[IdentifierType.COMPOSITE],
        Field(IdentifierType.COMPOSITE, description="Identifier's type"),
    ] = IdentifierType.COMPOSITE
    value: Annotated[CompositeIdentifier, Field(..., description="Identifier's value")]


AnyOrganizationRelationIdentifier = (
    OrganizationRelationIdentifier
    | IdOrganizationRelationIdentifier
    | UUIDOrganizationRelationIdentifier
    | CompositeOrganizationRelationIdentifier
)


def is_id_identifier(
    identifier: AnyOrganizationRelationIdentifier,
) -> TypeGuard[IdOrganizationRelationIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyOrganizationRelationIdentifier,
) -> TypeGuard[UUIDOrganizationRelationIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_composite_identifier(
    identifier: AnyOrganizationRelationIdentifier,
) -> TypeGuard[CompositeOrganizationRelationIdentifier]:
    return identifier.type is IdentifierType.COMPOSITE and isinstance(
        identifier.value, tuple
    )
