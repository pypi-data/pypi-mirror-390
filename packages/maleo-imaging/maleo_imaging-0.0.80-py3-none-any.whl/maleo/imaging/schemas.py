from pydantic import BaseModel, Field
from typing import Annotated, Generic, TypeVar
from maleo.types.integer import DoubleInts
from maleo.types.misc import StrOrStrEnumT


class ImageSize(BaseModel):
    height: Annotated[int, Field(..., description="Height", ge=0)]
    width: Annotated[int, Field(..., description="Width", ge=0)]

    @property
    def shape(self) -> DoubleInts:
        return (self.height, self.width)

    @classmethod
    def from_shape(cls, shape: DoubleInts) -> "ImageSize":
        return cls(height=shape[0], width=shape[1])


class BoundingBox(BaseModel):
    x_min: Annotated[float, Field(0.0, description="X Min", ge=0.0)]
    y_min: Annotated[float, Field(0.0, description="Y Min", ge=0.0)]
    x_max: Annotated[float, Field(0.0, description="X Max", ge=0.0)]
    y_max: Annotated[float, Field(0.0, description="Y Max", ge=0.0)]


OptionalBoundingBox = BoundingBox | None
OptionalBoundingBoxT = TypeVar("OptionalBoundingBoxT", bound=OptionalBoundingBox)


class Finding(BaseModel, Generic[StrOrStrEnumT, OptionalBoundingBoxT]):
    id: Annotated[int, Field(..., description="Finding's ID")]
    name: Annotated[StrOrStrEnumT, Field(..., description="Finding's Name")]
    confidence: Annotated[float, Field(..., description="Confidence", ge=0.0, le=1.0)]
    box: Annotated[OptionalBoundingBoxT, Field(..., description="Bounding Box")]


class FindingWithoutBox(Finding[StrOrStrEnumT, None], Generic[StrOrStrEnumT]):
    box: Annotated[None, Field(None, description="Bounding Box")] = None


class FindingWithBox(Finding[StrOrStrEnumT, BoundingBox], Generic[StrOrStrEnumT]):
    box: Annotated[BoundingBox, Field(..., description="Bounding Box")]


AnyFinding = FindingWithoutBox | FindingWithBox
AnyFindingT = TypeVar("AnyFindingT", bound=AnyFinding)
OptionalAnyFinding = AnyFinding | None
OptionalAnyFindingT = TypeVar("OptionalAnyFindingT", bound=OptionalAnyFinding)
