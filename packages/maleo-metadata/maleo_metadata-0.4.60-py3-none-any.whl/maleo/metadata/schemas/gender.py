from pydantic import BaseModel, Field
from typing import Generic, Literal, Sequence, Type, TypeVar, overload
from uuid import UUID
from maleo.enums.identity import Gender, ListOfGenders
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
from ..enums.gender import IdentifierType
from ..mixins.gender import Key, Name, GenderIdentifier
from ..types.gender import IdentifierValueType


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


class ReadSingleParameter(BaseReadSingleParameter[GenderIdentifier]):
    @classmethod
    def from_identifier(
        cls,
        identifier: GenderIdentifier,
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
            identifier=GenderIdentifier(type=identifier_type, value=identifier_value),
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
    IdentifierMixin[GenderIdentifier],
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
            identifier=GenderIdentifier(type=identifier_type, value=identifier_value),
            data=data,
        )


class StatusUpdateParameter(
    BaseStatusUpdateParameter[GenderIdentifier],
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
            identifier=GenderIdentifier(type=identifier_type, value=identifier_value),
            type=type,
        )


class DeleteSingleParameter(BaseDeleteSingleParameter[GenderIdentifier]):
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
            identifier=GenderIdentifier(type=identifier_type, value=identifier_value)
        )


class BaseGenderSchema(
    Name[str],
    Key,
    Order[OptInt],
):
    pass


class StandardGenderSchema(
    BaseGenderSchema,
    SimpleDataStatusMixin[DataStatus],
    LifecycleTimestamp,
    DataIdentifier,
):
    pass


OptStandardGenderSchema = StandardGenderSchema | None
ListOfStandardGenderSchemas = list[StandardGenderSchema]
SeqOfStandardGenderSchemas = Sequence[StandardGenderSchema]

KeyOrStandardSchema = Gender | StandardGenderSchema
OptKeyOrStandardSchema = KeyOrStandardSchema | None


class FullGenderSchema(
    BaseGenderSchema,
    SimpleDataStatusMixin[DataStatus],
    DataTimestamp,
    DataIdentifier,
):
    pass


OptFullGenderSchema = FullGenderSchema | None
ListOfFullGenderSchemas = list[FullGenderSchema]
SeqOfFullGenderSchemas = Sequence[FullGenderSchema]

KeyOrFullSchema = Gender | FullGenderSchema
OptKeyOrFullSchema = KeyOrFullSchema | None


AnyGenderSchemaType = Type[StandardGenderSchema] | Type[FullGenderSchema]


# Gender Schemas
AnyGenderSchema = StandardGenderSchema | FullGenderSchema
GenderSchemaT = TypeVar("GenderSchemaT", bound=AnyGenderSchema)

OptAnyGenderSchema = AnyGenderSchema | None
OptGenderSchemaT = TypeVar("OptGenderSchemaT", bound=OptAnyGenderSchema)

ListOfAnyGenderSchemas = ListOfStandardGenderSchemas | ListOfFullGenderSchemas
ListOfAnyGenderSchemasT = TypeVar(
    "ListOfAnyGenderSchemasT", bound=ListOfAnyGenderSchemas
)

OptListOfAnyGenderSchemas = ListOfAnyGenderSchemas | None
OptListOfAnyGenderSchemasT = TypeVar(
    "OptListOfAnyGenderSchemasT", bound=OptListOfAnyGenderSchemas
)


# Gender key and Schemas
AnyGender = Gender | AnyGenderSchema
AnyGenderT = TypeVar("AnyGenderT", bound=AnyGender)

OptAnyGender = AnyGender | None
OptAnyGenderT = TypeVar("OptAnyGenderT", bound=OptAnyGender)

ListOfAnyGenders = ListOfGenders | ListOfAnyGenderSchemas
ListOfAnyGendersT = TypeVar("ListOfAnyGendersT", bound=ListOfAnyGenders)

OptListOfAnyGenders = ListOfAnyGenders | None
OptListOfAnyGendersT = TypeVar("OptListOfAnyGendersT", bound=OptListOfAnyGenders)


class FullGenderMixin(BaseModel, Generic[OptAnyGenderT]):
    gender: OptAnyGenderT = Field(..., description="Gender")


class FullGendersMixin(BaseModel, Generic[OptListOfAnyGendersT]):
    genders: OptListOfAnyGendersT = Field(..., description="Genders")
