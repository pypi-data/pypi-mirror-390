from maleo.schemas.resource import Resource, ResourceIdentifier
from maleo.types.string import DoubleStrs


USER_SYSTEM_ROLE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_system_roles",
            name="User System Roles",
            slug="user-system-roles",
        )
    ],
    details=None,
)


COMPOSITE_COLUMS: DoubleStrs = ("user_id", "system_role")
