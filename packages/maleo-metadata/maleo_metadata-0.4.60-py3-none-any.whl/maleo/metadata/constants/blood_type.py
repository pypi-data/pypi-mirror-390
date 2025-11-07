from maleo.schemas.resource import Resource, ResourceIdentifier


BLOOD_TYPE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(key="blood_types", name="Blood Types", slug="blood-types")
    ],
    details=None,
)
