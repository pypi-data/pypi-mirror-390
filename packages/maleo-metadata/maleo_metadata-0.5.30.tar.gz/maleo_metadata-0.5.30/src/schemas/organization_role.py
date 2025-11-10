from pydantic import BaseModel, Field
from typing import Generic, Literal, Sequence, Type, TypeVar, overload
from uuid import UUID
from maleo.enums.organization import OrganizationRole, ListOfOrganizationRoles
from maleo.enums.status import (
    DataStatus,
    ListOfDataStatuses,
    SimpleDataStatusMixin,
    FULL_DATA_STATUSES,
)
from maleo.schemas.mixins.filter import convert as convert_filter
from maleo.schemas.mixins.general import Order
from maleo.schemas.mixins.identity import (
    IdentifierMixin,
    DataIdentifier,
    Ids,
    UUIDs,
    Keys,
    Names,
)
from maleo.schemas.mixins.sort import convert as convert_sort
from maleo.schemas.mixins.timestamp import LifecycleTimestamp, DataTimestamp
from maleo.schemas.operation.enums import ResourceOperationStatusUpdateType
from maleo.schemas.parameter import (
    ReadSingleParameter as BaseReadSingleParameter,
    ReadPaginatedMultipleParameter,
    StatusUpdateParameter as BaseStatusUpdateParameter,
    DeleteSingleParameter as BaseDeleteSingleParameter,
)
from maleo.types.dict import StrToAnyDict
from maleo.types.integer import OptInt, OptListOfInts
from maleo.types.string import OptListOfStrs, OptStr
from maleo.types.uuid import OptListOfUUIDs
from ..enums.organization_role import IdentifierType
from ..mixins.organization_role import Key, Name, OrganizationRoleIdentifier
from ..types.organization_role import IdentifierValueType


class CreateData(Name[str], Key, Order[OptInt]):
    pass


class CreateDataMixin(BaseModel):
    data: CreateData = Field(..., description="Create data")


class CreateParameter(
    CreateDataMixin,
):
    pass


class ReadMultipleParameter(
    ReadPaginatedMultipleParameter,
    Names[OptListOfStrs],
    Keys[OptListOfStrs],
    UUIDs[OptListOfUUIDs],
    Ids[OptListOfInts],
):
    @property
    def _query_param_fields(self) -> set[str]:
        return {
            "ids",
            "uuids",
            "statuses",
            "keys",
            "names",
            "search",
            "page",
            "limit",
            "granularity",
            "use_cache",
        }

    def to_query_params(self) -> StrToAnyDict:
        params = self.model_dump(
            mode="json", include=self._query_param_fields, exclude_none=True
        )
        params["filters"] = convert_filter(self.date_filters)
        params["sorts"] = convert_sort(self.sort_columns)
        params = {k: v for k, v in params.items()}
        return params


class ReadSingleParameter(BaseReadSingleParameter[OrganizationRoleIdentifier]):
    @classmethod
    def from_identifier(
        cls,
        identifier: OrganizationRoleIdentifier,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter":
        return cls(identifier=identifier, statuses=statuses, use_cache=use_cache)

    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.KEY, IdentifierType.NAME],
        identifier_value: str,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        statuses: ListOfDataStatuses = FULL_DATA_STATUSES,
        use_cache: bool = True,
    ) -> "ReadSingleParameter":
        return cls(
            identifier=OrganizationRoleIdentifier(
                type=identifier_type, value=identifier_value
            ),
            statuses=statuses,
            use_cache=use_cache,
        )

    def to_query_params(self) -> StrToAnyDict:
        return self.model_dump(
            mode="json", include={"statuses", "use_cache"}, exclude_none=True
        )


class FullUpdateData(Name[str], Order[OptInt]):
    pass


class PartialUpdateData(Name[OptStr], Order[OptInt]):
    pass


UpdateDataT = TypeVar("UpdateDataT", FullUpdateData, PartialUpdateData)


class UpdateDataMixin(BaseModel, Generic[UpdateDataT]):
    data: UpdateDataT = Field(..., description="Update data")


class UpdateParameter(
    UpdateDataMixin[UpdateDataT],
    IdentifierMixin[OrganizationRoleIdentifier],
    Generic[UpdateDataT],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        data: UpdateDataT,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        data: UpdateDataT,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.KEY, IdentifierType.NAME],
        identifier_value: str,
        data: UpdateDataT,
    ) -> "UpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
    ) -> "UpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        data: UpdateDataT,
    ) -> "UpdateParameter":
        return cls(
            identifier=OrganizationRoleIdentifier(
                type=identifier_type, value=identifier_value
            ),
            data=data,
        )


class StatusUpdateParameter(
    BaseStatusUpdateParameter[OrganizationRoleIdentifier],
):
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.ID],
        identifier_value: int,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.UUID],
        identifier_value: UUID,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.KEY, IdentifierType.NAME],
        identifier_value: str,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter": ...
    @classmethod
    def new(
        cls,
        identifier_type: IdentifierType,
        identifier_value: IdentifierValueType,
        type: ResourceOperationStatusUpdateType,
    ) -> "StatusUpdateParameter":
        return cls(
            identifier=OrganizationRoleIdentifier(
                type=identifier_type, value=identifier_value
            ),
            type=type,
        )


class DeleteSingleParameter(BaseDeleteSingleParameter[OrganizationRoleIdentifier]):
    @overload
    @classmethod
    def new(
        cls, identifier_type: Literal[IdentifierType.ID], identifier_value: int
    ) -> "DeleteSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls, identifier_type: Literal[IdentifierType.UUID], identifier_value: UUID
    ) -> "DeleteSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls,
        identifier_type: Literal[IdentifierType.KEY, IdentifierType.NAME],
        identifier_value: str,
    ) -> "DeleteSingleParameter": ...
    @overload
    @classmethod
    def new(
        cls, identifier_type: IdentifierType, identifier_value: IdentifierValueType
    ) -> "DeleteSingleParameter": ...
    @classmethod
    def new(
        cls, identifier_type: IdentifierType, identifier_value: IdentifierValueType
    ) -> "DeleteSingleParameter":
        return cls(
            identifier=OrganizationRoleIdentifier(
                type=identifier_type, value=identifier_value
            )
        )


class BaseOrganizationRoleSchema(
    Name[str],
    Key,
    Order[OptInt],
):
    pass


class StandardOrganizationRoleSchema(
    BaseOrganizationRoleSchema,
    SimpleDataStatusMixin[DataStatus],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


OptStandardOrganizationRoleSchema = StandardOrganizationRoleSchema | None
ListOfStandardOrganizationRoleSchemas = list[StandardOrganizationRoleSchema]
SeqOfStandardOrganizationRoleSchemas = Sequence[StandardOrganizationRoleSchema]

KeyOrStandardSchema = OrganizationRole | StandardOrganizationRoleSchema
OptKeyOrStandardSchema = KeyOrStandardSchema | None


class FullOrganizationRoleSchema(
    BaseOrganizationRoleSchema,
    SimpleDataStatusMixin[DataStatus],
    DataTimestamp,
    DataIdentifier,
):
    pass


OptFullOrganizationRoleSchema = FullOrganizationRoleSchema | None
ListOfFullOrganizationRoleSchemas = list[FullOrganizationRoleSchema]
SeqOfFullOrganizationRoleSchemas = Sequence[FullOrganizationRoleSchema]

KeyOrFullSchema = OrganizationRole | FullOrganizationRoleSchema
OptKeyOrFullSchema = KeyOrFullSchema | None


AnyOrganizationRoleSchemaType = (
    Type[StandardOrganizationRoleSchema] | Type[FullOrganizationRoleSchema]
)


# Organization Role Schemas
AnyOrganizationRoleSchema = StandardOrganizationRoleSchema | FullOrganizationRoleSchema
OrganizationRoleSchemaT = TypeVar(
    "OrganizationRoleSchemaT", bound=AnyOrganizationRoleSchema
)

OptAnyOrganizationRoleSchema = AnyOrganizationRoleSchema | None
OptOrganizationRoleSchemaT = TypeVar(
    "OptOrganizationRoleSchemaT", bound=OptAnyOrganizationRoleSchema
)

ListOfAnyOrganizationRoleSchemas = (
    ListOfStandardOrganizationRoleSchemas | ListOfFullOrganizationRoleSchemas
)
ListOfAnyOrganizationRoleSchemasT = TypeVar(
    "ListOfAnyOrganizationRoleSchemasT", bound=ListOfAnyOrganizationRoleSchemas
)

OptListOfAnyOrganizationRoleSchemas = ListOfAnyOrganizationRoleSchemas | None
OptListOfAnyOrganizationRoleSchemasT = TypeVar(
    "OptListOfAnyOrganizationRoleSchemasT", bound=OptListOfAnyOrganizationRoleSchemas
)


# Organization Role key and Schemas
AnyOrganizationRole = OrganizationRole | AnyOrganizationRoleSchema
AnyOrganizationRoleT = TypeVar("AnyOrganizationRoleT", bound=AnyOrganizationRole)

OptAnyOrganizationRole = AnyOrganizationRole | None
OptAnyOrganizationRoleT = TypeVar(
    "OptAnyOrganizationRoleT", bound=OptAnyOrganizationRole
)

ListOfAnyOrganizationRoles = ListOfOrganizationRoles | ListOfAnyOrganizationRoleSchemas
ListOfAnyOrganizationRolesT = TypeVar(
    "ListOfAnyOrganizationRolesT", bound=ListOfAnyOrganizationRoles
)

OptListOfAnyOrganizationRoles = ListOfAnyOrganizationRoles | None
OptListOfAnyOrganizationRolesT = TypeVar(
    "OptListOfAnyOrganizationRolesT", bound=OptListOfAnyOrganizationRoles
)


class SimpleOrganizationRoleMixin(BaseModel, Generic[OptAnyOrganizationRoleT]):
    role: OptAnyOrganizationRoleT = Field(..., description="Organization role")


class FullOrganizationRoleMixin(BaseModel, Generic[OptAnyOrganizationRoleT]):
    organization_role: OptAnyOrganizationRoleT = Field(
        ..., description="Organization role"
    )


class SimpleOrganizationRolesMixin(BaseModel, Generic[OptListOfAnyOrganizationRolesT]):
    roles: OptListOfAnyOrganizationRolesT = Field(..., description="Organization roles")


class FullOrganizationRolesMixin(BaseModel, Generic[OptListOfAnyOrganizationRolesT]):
    organization_roles: OptListOfAnyOrganizationRolesT = Field(
        ..., description="Organization roles"
    )
