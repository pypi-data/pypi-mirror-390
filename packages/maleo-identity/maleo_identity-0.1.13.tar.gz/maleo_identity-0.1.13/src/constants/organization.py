from maleo.schemas.resource import Resource, ResourceIdentifier


ORGANIZATION_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organizations", name="Organizations", slug="organizations"
        )
    ],
    details=None,
)
