from datetime import date
from pydantic import BaseModel, Field
from typing import Annotated, Generic, TypeVar, Type
from maleo.enums.identity import (
    OptBloodType,
    BloodTypeMixin,
    OptRhesus,
    RhesusMixin,
    Gender,
    OptGender,
    GenderMixin,
)
from maleo.enums.medical import MedicalRole, FullMedicalRoleMixin
from maleo.enums.organization import (
    OrganizationRole,
    FullOrganizationRoleMixin,
    OrganizationType,
    FullOrganizationTypeMixin,
)
from maleo.enums.status import DataStatus as DataStatusEnum, SimpleDataStatusMixin
from maleo.enums.system import SystemRole, FullSystemRoleMixin
from maleo.enums.user import UserType, FullUserTypeMixin
from maleo.schemas.mixins.identity import (
    DataIdentifier,
    IntOrganizationId,
    IntUserId,
    BirthDate,
    DateOfBirth,
)
from maleo.schemas.mixins.timestamp import LifecycleTimestamp
from maleo.types.datetime import OptDate
from maleo.types.integer import OptInt
from maleo.types.string import OptStr
from ..mixins.common import IdCard, FullName, BirthPlace, PlaceOfBirth
from ..mixins.api_key import APIKey
from ..mixins.organization_registration_code import Code, CurrentUses
from ..mixins.organization_relation import IsBidirectional, Meta
from ..mixins.organization import Key as OrganizationKey, Name as OrganizationName
from ..mixins.patient import PatientIdentity
from ..mixins.user_profile import (
    LeadingTitle,
    FirstName,
    MiddleName,
    LastName,
    EndingTitle,
    AvatarName,
    AvatarUrl,
)
from ..mixins.user import Username, Email, Phone


class APIKeySchema(
    APIKey,
    IntOrganizationId[OptInt],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class PatientSchema(
    RhesusMixin[OptRhesus],
    BloodTypeMixin[OptBloodType],
    GenderMixin[Gender],
    DateOfBirth[date],
    PlaceOfBirth[OptStr],
    FullName[str],
    PatientIdentity,
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class OrganizationRegistrationCodeSchema(
    CurrentUses,
    Code[str],
    IntOrganizationId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


OptOrganizationRegistrationCodeSchema = OrganizationRegistrationCodeSchema | None


class OrganizationRegistrationCodeSchemaMixin(BaseModel):
    registration_code: Annotated[
        OptOrganizationRegistrationCodeSchema,
        Field(None, description="Organization's registration code"),
    ] = None


class StandardOrganizationSchema(
    OrganizationName[str],
    OrganizationKey[str],
    FullOrganizationTypeMixin[OrganizationType],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class SourceOrganizationSchemaMixin(BaseModel):
    source: Annotated[
        StandardOrganizationSchema, Field(..., description="Source organization")
    ]


class SourceOrganizationRelationSchema(
    Meta,
    IsBidirectional[bool],
    SourceOrganizationSchemaMixin,
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class SourceOrganizationRelationsSchemaMixin(BaseModel):
    sources: Annotated[
        list[SourceOrganizationRelationSchema],
        Field(list[SourceOrganizationRelationSchema](), description="Sources"),
    ] = list[SourceOrganizationRelationSchema]()


class TargetOrganizationSchemaMixin(BaseModel):
    target: Annotated[
        StandardOrganizationSchema, Field(..., description="Target organization")
    ]


class TargetOrganizationRelationSchema(
    Meta,
    IsBidirectional[bool],
    TargetOrganizationSchemaMixin,
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class TargetOrganizationRelationsSchemaMixin(BaseModel):
    targets: Annotated[
        list[TargetOrganizationRelationSchema],
        Field(list[TargetOrganizationRelationSchema](), description="Targets"),
    ] = list[TargetOrganizationRelationSchema]()


class FullOrganizationSchema(
    TargetOrganizationRelationsSchemaMixin,
    SourceOrganizationRelationsSchemaMixin,
    OrganizationRegistrationCodeSchemaMixin,
    StandardOrganizationSchema,
):
    pass


AnyOrganizationSchemaType = (
    Type[StandardOrganizationSchema] | Type[FullOrganizationSchema]
)
AnyOrganizationSchema = StandardOrganizationSchema | FullOrganizationSchema
AnyOrganizationSchemaT = TypeVar("AnyOrganizationSchemaT", bound=AnyOrganizationSchema)


class OrganizationSchemaMixin(BaseModel, Generic[AnyOrganizationSchemaT]):
    organization: Annotated[
        AnyOrganizationSchemaT, Field(..., description="Organization")
    ]


class UserMedicalRoleSchema(
    FullMedicalRoleMixin[MedicalRole],
    IntOrganizationId[int],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class UserMedicalRolesSchemaMixin(BaseModel):
    medical_roles: Annotated[
        list[UserMedicalRoleSchema],
        Field(list[UserMedicalRoleSchema](), description="Medical roles"),
    ] = list[UserMedicalRoleSchema]()


class UserOrganizationRoleSchema(
    FullOrganizationRoleMixin[OrganizationRole],
    IntOrganizationId[int],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class UserOrganizationRolesSchemaMixin(BaseModel):
    organization_roles: Annotated[
        list[UserOrganizationRoleSchema],
        Field(list[UserOrganizationRoleSchema](), description="Organization roles"),
    ] = list[UserOrganizationRoleSchema]()


class UserProfileSchema(
    AvatarUrl[OptStr],
    AvatarName[str],
    BloodTypeMixin[OptBloodType],
    GenderMixin[OptGender],
    BirthDate[OptDate],
    BirthPlace[OptStr],
    FullName[str],
    EndingTitle[OptStr],
    LastName[str],
    MiddleName[OptStr],
    FirstName[str],
    LeadingTitle[OptStr],
    IdCard[OptStr],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


OptUserProfileSchema = UserProfileSchema | None


class UserProfileSchemaMixin(BaseModel):
    profile: Annotated[
        OptUserProfileSchema, Field(None, description="User's Profile")
    ] = None


class UserSystemRoleSchema(
    FullSystemRoleMixin[SystemRole],
    IntUserId[int],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class UserSystemRolesSchemaMixin(BaseModel):
    system_roles: Annotated[
        list[UserSystemRoleSchema],
        Field(
            list[UserSystemRoleSchema](),
            description="User's system roles",
            min_length=1,
        ),
    ] = list[UserSystemRoleSchema]()


class StandardUserSchema(
    UserProfileSchemaMixin,
    Phone[str],
    Email[str],
    Username[str],
    FullUserTypeMixin[UserType],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class UserOrganizationSchema(
    UserMedicalRolesSchemaMixin,
    UserOrganizationRolesSchemaMixin,
    OrganizationSchemaMixin[StandardOrganizationSchema],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


class UserOrganizationsSchemaMixin(BaseModel):
    organizations: Annotated[
        list[UserOrganizationSchema],
        Field(list[UserOrganizationSchema](), description="Organizations"),
    ] = list[UserOrganizationSchema]()


class FullUserSchema(UserSystemRolesSchemaMixin, StandardUserSchema):
    pass


AnyUserSchemaType = Type[StandardUserSchema] | Type[FullUserSchema]
AnyUserSchema = StandardUserSchema | FullUserSchema
AnyUserSchemaT = TypeVar("AnyUserSchemaT", bound=AnyUserSchema)


class UserSchemaMixin(BaseModel, Generic[AnyUserSchemaT]):
    user: Annotated[AnyUserSchemaT, Field(..., description="User")]


class UserAndOrganizationSchema(
    UserMedicalRolesSchemaMixin,
    UserOrganizationRolesSchemaMixin,
    OrganizationSchemaMixin[StandardOrganizationSchema],
    UserSchemaMixin[StandardUserSchema],
    SimpleDataStatusMixin[DataStatusEnum],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass
