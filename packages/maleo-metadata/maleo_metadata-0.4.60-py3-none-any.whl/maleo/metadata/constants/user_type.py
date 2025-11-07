from maleo.schemas.resource import Resource, ResourceIdentifier


USER_TYPE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(key="user_types", name="User Types", slug="user-types")
    ],
    details=None,
)
