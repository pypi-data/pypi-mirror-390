from maleo.schemas.resource import Resource, ResourceIdentifier


ORGANIZATION_REGISTRATION_CODE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organization_registration_codes",
            name="Organization Registration Codes",
            slug="organization-registration-codes",
        )
    ],
    details=None,
)
