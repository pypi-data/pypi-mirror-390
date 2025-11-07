from maleo.schemas.resource import Resource, ResourceIdentifier


MEDICAL_SERVICE_RESOURCE = Resource(
    identifiers=[
        ResourceIdentifier(
            key="medical_services", name="Medical Services", slug="medical-services"
        )
    ],
    details=None,
)
