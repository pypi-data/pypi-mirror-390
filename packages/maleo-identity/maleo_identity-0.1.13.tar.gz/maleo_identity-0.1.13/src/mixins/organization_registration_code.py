from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from maleo.schemas.mixins.identity import Identifier
from maleo.types.integer import OptIntT
from maleo.types.string import OptStrT
from ..enums.organization_registration_code import IdentifierType
from ..types.organization_registration_code import IdentifierValueType


class Code(BaseModel, Generic[OptStrT]):
    code: Annotated[OptStrT, Field(..., description="Code", max_length=36)]


class MaxUses(BaseModel, Generic[OptIntT]):
    max_uses: Annotated[OptIntT, Field(..., description="Max Uses", ge=1)]


class CurrentUses(BaseModel):
    current_uses: Annotated[int, Field(0, description="Current Uses", ge=0)] = 0


class OrganizationRegistrationCodeIdentifier(
    Identifier[IdentifierType, IdentifierValueType]
):
    pass


class IdOrganizationRegistrationCodeIdentifier(
    Identifier[Literal[IdentifierType.ID], int]
):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class OrgIdOrganizationRegistrationCodeIdentifier(
    Identifier[Literal[IdentifierType.ORGANIZATION_ID], int]
):
    type: Annotated[
        Literal[IdentifierType.ORGANIZATION_ID],
        Field(IdentifierType.ORGANIZATION_ID, description="Identifier's type"),
    ] = IdentifierType.ORGANIZATION_ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDOrganizationRegistrationCodeIdentifier(
    Identifier[Literal[IdentifierType.UUID], UUID]
):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class CodeOrganizationRegistrationCodeIdentifier(
    Identifier[Literal[IdentifierType.CODE], str]
):
    type: Annotated[
        Literal[IdentifierType.CODE],
        Field(IdentifierType.CODE, description="Identifier's type"),
    ] = IdentifierType.CODE
    value: Annotated[str, Field(..., description="Identifier's value", max_length=36)]


AnyOrganizationRegistrationCodeIdentifier = (
    OrganizationRegistrationCodeIdentifier
    | IdOrganizationRegistrationCodeIdentifier
    | OrgIdOrganizationRegistrationCodeIdentifier
    | UUIDOrganizationRegistrationCodeIdentifier
    | CodeOrganizationRegistrationCodeIdentifier
)


def is_id_identifier(
    identifier: AnyOrganizationRegistrationCodeIdentifier,
) -> TypeGuard[IdOrganizationRegistrationCodeIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_org_id_identifier(
    identifier: AnyOrganizationRegistrationCodeIdentifier,
) -> TypeGuard[OrgIdOrganizationRegistrationCodeIdentifier]:
    return identifier.type is IdentifierType.ORGANIZATION_ID and isinstance(
        identifier.value, int
    )


def is_uuid_identifier(
    identifier: AnyOrganizationRegistrationCodeIdentifier,
) -> TypeGuard[UUIDOrganizationRegistrationCodeIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_code_identifier(
    identifier: AnyOrganizationRegistrationCodeIdentifier,
) -> TypeGuard[CodeOrganizationRegistrationCodeIdentifier]:
    return identifier.type is IdentifierType.CODE and isinstance(identifier.value, str)
