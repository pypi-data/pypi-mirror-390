from datetime import date
from sqlalchemy import CheckConstraint, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID as PostgreSQLUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import Boolean, Date, Enum, Integer, String, Text
from uuid import UUID, uuid4
from maleo.enums.identity import (
    BloodType,
    OptBloodType,
    Rhesus,
    OptRhesus,
    Gender,
    OptGender,
)
from maleo.enums.organization import (
    OrganizationType,
    OrganizationRelation as OrganizationRelationEnum,
    OrganizationRole,
)
from maleo.enums.medical import MedicalRole
from maleo.enums.system import SystemRole
from maleo.enums.user import UserType
from maleo.schemas.model import DataIdentifier, DataStatus, DataTimestamp
from maleo.types.integer import OptInt
from maleo.types.misc import OptListOfAnyOrStrToAnyDict
from maleo.types.string import OptStr


class APIKey(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "api_keys"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    organization_id: Mapped[OptInt] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
    )

    api_key: Mapped[str] = mapped_column(
        name="api_key", type_=String(255), unique=True, nullable=False
    )

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_organization"),
    )


class Patient(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "patients"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    id_card: Mapped[OptStr] = mapped_column(
        name="id_card", type_=String(16), unique=True
    )
    passport: Mapped[OptStr] = mapped_column(
        name="passport", type_=String(9), unique=True
    )
    full_name: Mapped[str] = mapped_column(
        name="full_name", type_=String(200), nullable=False
    )
    place_of_birth: Mapped[OptStr] = mapped_column(
        name="place_of_birth", type_=String(50)
    )
    date_of_birth: Mapped[date] = mapped_column(
        name="date_of_birth", type_=Date, nullable=False
    )
    gender: Mapped[Gender] = mapped_column(
        name="gender", type_=Enum(Gender, name="gender"), nullable=False
    )
    blood_type: Mapped[OptBloodType] = mapped_column(
        name="blood_type", type_=Enum(BloodType, name="blood_type")
    )
    rhesus: Mapped[OptRhesus] = mapped_column(
        name="rhesus", type_=Enum(Rhesus, name="rhesus")
    )

    __table_args__ = (
        CheckConstraint(
            "id_card IS NOT NULL OR passport IS NOT NULL",
            name="chk_id_card_or_passport",
        ),
    )


class OrganizationRegistrationCode(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "organization_registration_codes"
    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        unique=True,
        nullable=False,
    )
    code: Mapped[str] = mapped_column(
        name="code", type_=String(36), unique=True, nullable=False
    )
    current_uses: Mapped[int] = mapped_column(
        name="current_uses", type_=Integer, nullable=False, default=0
    )


class OrganizationRelation(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "organization_relations"
    source_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    target_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    relation: Mapped[OrganizationRelationEnum] = mapped_column(
        name="relation",
        type_=Enum(OrganizationRelationEnum, name="organization_relation"),
        nullable=False,
    )
    is_bidirectional: Mapped[bool] = mapped_column(
        name="is_bidirectional", type_=Boolean, default=False, nullable=False
    )
    meta: Mapped[OptListOfAnyOrStrToAnyDict] = mapped_column(
        name="meta", type_=JSONB, default=None
    )


class Organization(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "organizations"
    organization_type: Mapped[OrganizationType] = mapped_column(
        name="organization_type",
        type_=Enum(OrganizationType, name="organization_type"),
        default=OrganizationType.REGULAR,
        nullable=False,
    )
    key: Mapped[str] = mapped_column(
        name="key", type_=String(255), unique=True, nullable=False
    )
    name: Mapped[str] = mapped_column(name="name", type_=String(255), nullable=False)
    secret: Mapped[UUID] = mapped_column(
        name="secret",
        type_=PostgreSQLUUID(as_uuid=True),
        default=uuid4,
        unique=True,
        nullable=False,
    )


class UserMedicalRole(DataStatus, DataTimestamp, DataIdentifier):
    __tablename__ = "user_medical_roles"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    medical_role: Mapped[MedicalRole] = mapped_column(
        name="medical_role",
        type_=Enum(MedicalRole, name="medical_role"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id", "organization_id", "medical_role", name="uq_user_medical_role"
        ),
    )


class UserOrganizationRole(DataStatus, DataTimestamp, DataIdentifier):
    __tablename__ = "user_organization_roles_v2"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    organization_role: Mapped[OrganizationRole] = mapped_column(
        name="organization_role",
        type_=Enum(OrganizationRole, name="organization_role"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "organization_id",
            "organization_role",
            name="uq_user_organization_role",
        ),
    )


class UserProfile(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "user_profiles"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    id_card: Mapped[OptStr] = mapped_column(name="id_card", type_=String(16))
    leading_title: Mapped[OptStr] = mapped_column(
        name="leading_title", type_=String(25)
    )
    first_name: Mapped[str] = mapped_column(
        name="first_name", type_=String(50), nullable=False
    )
    middle_name: Mapped[OptStr] = mapped_column(name="middle_name", type_=String(50))
    last_name: Mapped[str] = mapped_column(
        name="last_name", type_=String(50), nullable=False
    )
    ending_title: Mapped[OptStr] = mapped_column(name="ending_title", type_=String(25))
    full_name: Mapped[str] = mapped_column(
        name="full_name", type_=String(200), nullable=False
    )
    birth_place: Mapped[OptStr] = mapped_column(name="birth_place", type_=String(50))
    birth_date: Mapped[date] = mapped_column(name="birth_date", type_=Date)
    gender: Mapped[OptGender] = mapped_column(
        name="gender", type_=Enum(Gender, name="gender")
    )
    blood_type: Mapped[OptBloodType] = mapped_column(
        name="blood_type", type_=Enum(BloodType, name="blood_type")
    )
    avatar_name: Mapped[str] = mapped_column(
        name="avatar_name", type_=Text, nullable=False
    )


class UserSystemRole(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "user_system_roles"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    system_role: Mapped[SystemRole] = mapped_column(
        name="system_role",
        type_=Enum(SystemRole, name="system_role"),
        default=SystemRole.USER,
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "system_role", name="uq_user_system_role"),
    )


class User(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "users"
    user_type: Mapped[UserType] = mapped_column(
        name="user_type",
        type_=Enum(UserType, name="user_type"),
        default=UserType.REGULAR,
        nullable=False,
    )
    username: Mapped[str] = mapped_column(
        name="username", type_=String(50), unique=True, nullable=False
    )
    email: Mapped[str] = mapped_column(
        name="email", type_=String(255), unique=True, nullable=False
    )
    phone: Mapped[str] = mapped_column(name="phone", type_=String(15), nullable=False)
    password: Mapped[str] = mapped_column(
        name="password", type_=String(255), nullable=False
    )


class UserOrganization(
    DataStatus,
    DataTimestamp,
    DataIdentifier,
):
    __tablename__ = "user_organizations"
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    organization_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("organizations.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_organization"),
    )
