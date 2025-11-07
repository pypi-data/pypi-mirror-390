from maleo.schemas.resource import Resource, ResourceIdentifier


MEDICAL_ROLE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="medical_roles", name="Medical Roles", slug="medical-roles"
        )
    ],
    details=None,
)
