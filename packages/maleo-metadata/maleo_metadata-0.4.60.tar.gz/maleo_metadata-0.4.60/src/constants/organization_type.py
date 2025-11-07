from maleo.schemas.resource import Resource, ResourceIdentifier


ORGANIZATION_TYPE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="organization_types",
            name="Organization Types",
            slug="organization-types",
        )
    ],
    details=None,
)
