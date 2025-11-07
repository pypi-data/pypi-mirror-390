from pydantic import Field
from typing import Annotated, Literal, TypeGuard
from uuid import UUID
from maleo.schemas.mixins.identity import Identifier
from ..enums.record_inference import IdentifierType
from ..types.record_inference import IdentifierValueType


class RecordInferenceIdentifier(Identifier[IdentifierType, IdentifierValueType]):
    @property
    def column_and_value(self) -> tuple[str, IdentifierValueType]:
        return self.type.column, self.value


class IdRecordInferenceIdentifier(Identifier[Literal[IdentifierType.ID], int]):
    type: Annotated[
        Literal[IdentifierType.ID],
        Field(IdentifierType.ID, description="Identifier's type"),
    ] = IdentifierType.ID
    value: Annotated[int, Field(..., description="Identifier's value", ge=1)]


class UUIDRecordInferenceIdentifier(Identifier[Literal[IdentifierType.UUID], UUID]):
    type: Annotated[
        Literal[IdentifierType.UUID],
        Field(IdentifierType.UUID, description="Identifier's type"),
    ] = IdentifierType.UUID


AnyRecordInferenceIdentifier = (
    RecordInferenceIdentifier
    | IdRecordInferenceIdentifier
    | UUIDRecordInferenceIdentifier
)


def is_id_identifier(
    identifier: AnyRecordInferenceIdentifier,
) -> TypeGuard[IdRecordInferenceIdentifier]:
    return identifier.type is IdentifierType.ID and isinstance(identifier.value, int)


def is_uuid_identifier(
    identifier: AnyRecordInferenceIdentifier,
) -> TypeGuard[UUIDRecordInferenceIdentifier]:
    return identifier.type is IdentifierType.UUID and isinstance(identifier.value, UUID)
