from maleo.schemas.resource import Resource, ResourceIdentifier


PATIENT_RESOURCE = Resource(
    identifiers=[ResourceIdentifier(key="patients", name="Patients", slug="patients")],
    details=None,
)
