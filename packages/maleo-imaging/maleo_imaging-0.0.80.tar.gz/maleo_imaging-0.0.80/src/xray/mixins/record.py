from pydantic import BaseModel, Field
from typing import Annotated, Generic, Literal, TypeGuard
from uuid import UUID
from maleo.schemas.mixins.identity import Identifier
from maleo.types.string import OptStr
from maleo.types.uuid import OptListOfUUIDsT
from ..enums.record import IdentifierType
from ..types.record import IdentifierValueType


class Name(BaseModel):
    name: Annotated[
        OptStr, Field(None, description="Patient's name", max_length=200)
    ] = None


class Description(BaseModel):
    description: Annotated[OptStr, Field(None, description="Imaging's description")] = (
        None
    )


class Impression(BaseModel):
    impression: Annotated[OptStr, Field(None, description="Imaging's name")] = None


class Diagnosis(BaseModel):
    diagnosis: Annotated[str, Field(..., description="Imaging's diagnosis")]


class RecordIds(BaseModel, Generic[OptListOfUUIDsT]):
    record_ids: Annotated[OptListOfUUIDsT, Field(..., description="Record's ids")]


class RecordIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdRecordIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDRecordIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


AnyRecordIdentifier = RecordIdentifier | IdRecordIdentifier | UUIDRecordIdentifier


def is_id_identifier(
    identifier: AnyRecordIdentifier,
) -> TypeGuard[IdRecordIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyRecordIdentifier,
) -> TypeGuard[UUIDRecordIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)
