from maleo.schemas.resource import Resource, ResourceIdentifier


USER_PROFILE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="user_profiles", name="User Profiles", slug="user-profiles"
        )
    ],
    details=None,
)
