from maleo.schemas.resource import Resource, ResourceIdentifier


API_KEY_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="api_keys",
            name="API Keys",
            slug="api-keys",
        )
    ],
    details=None,
)
