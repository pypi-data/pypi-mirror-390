from pydantic import Field, model_validator
from typing import Annotated, Generic, Literal, Self, TypeGuard
from uuid import UUID
from maleo.schemas.mixins.identity import Identifier
from maleo.schemas.mixins.identity import Passport as BasePassport
from maleo.types.string import OptStr, OptStrT
from ..enums.patient import IdentifierType
from ..types.patient import IdentifierValueType
from .common import IdCard


class Passport(BasePassport, Generic[OptStrT]):
    passport: Annotated[OptStrT, Field(..., description="Passport", max_length=9)]


class PatientIdentity(
    Passport[OptStr],
    IdCard[OptStr],
):
    @model_validator(mode="after")
    def chk_id_card_or_passport(self) -> Self:
        if self.id_card is None and self.passport is None:
            raise ValueError("Either ID Card or Passport must exist")
        return self


class PatientIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    pass


class IdPatientIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDPatientIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


class IdCardPatientIdentifier(Identifier[Literal[IdentifierType.ID_CARD], str]):
    type: Annotated[
        Literal[IdentifierType.ID_CARD],
        Field(IdentifierType.ID_CARD, description="Identifier's type"),
    ] = IdentifierType.ID_CARD
    value: Annotated[str, Field(..., description="Identifier's value", max_length=16)]


class PassportPatientIdentifier(Identifier[Literal[IdentifierType.PASSPORT], str]):
    type: Annotated[
        Literal[IdentifierType.PASSPORT],
        Field(IdentifierType.PASSPORT, description="Identifier's type"),
    ] = IdentifierType.PASSPORT
    value: Annotated[str, Field(..., description="Identifier's value", max_length=9)]


AnyPatientIdentifier = (
    PatientIdentifier
    | IdPatientIdentifier
    | UUIDPatientIdentifier
    | IdCardPatientIdentifier
    | PassportPatientIdentifier
)


def is_id_identifier(
    identifier: AnyPatientIdentifier,
) -> TypeGuard[IdPatientIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyPatientIdentifier,
) -> TypeGuard[UUIDPatientIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)


def is_id_card_identifier(
    identifier: AnyPatientIdentifier,
) -> TypeGuard[IdCardPatientIdentifier]:
    return identifier.type is IdentifierType.ID_CARD and isinstance(
        identifier.value, str
    )


def is_passport_identifier(
    identifier: AnyPatientIdentifier,
) -> TypeGuard[PassportPatientIdentifier]:
    return identifier.type is IdentifierType.PASSPORT and isinstance(
        identifier.value, str
    )
