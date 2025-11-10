from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from maleo.schemas.mixins.identity import Identifier
from maleo.types.uuid import OptListOfUUIDsT
from ..enums.inference import IdentifierType, OptionalListOfInferenceTypesT
from ..types.inference import IdentifierValueType


class InferenceIds(BaseModel, Generic[OptListOfUUIDsT]):
    inference_ids: Annotated[OptListOfUUIDsT, Field(..., description="Inference's ids")]


class InferenceTypes(BaseModel, Generic[OptionalListOfInferenceTypesT]):
    inference_types: Annotated[
        OptionalListOfInferenceTypesT, Field(..., description="Inference's types")
    ]


class InferenceIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdInferenceIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDInferenceIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


AnyInferenceIdentifier = (
    InferenceIdentifier | IdInferenceIdentifier | UUIDInferenceIdentifier
)


def is_id_identifier(
    identifier: AnyInferenceIdentifier,
) -> TypeGuard[IdInferenceIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyInferenceIdentifier,
) -> TypeGuard[UUIDInferenceIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)
