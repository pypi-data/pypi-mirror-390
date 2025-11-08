from typing_extensions import TypeAlias
from uuid import UUID


from .base import BlockbaxModel

from .data_types import (
    NumberTypeMixin,
    TextTypeMixin,
    LocationTypeMixin,
    MapLayerTypeMixin,
    ImageTypeMixin,
    AreaTypeMixin,
    UnknownTypeMixin,
)

from pydantic import TypeAdapter, field_validator


class SubjectPropertyBase(BlockbaxModel):
    type_id: UUID
    value_id: UUID | str | None = None
    caption: str | None = None
    inherit: bool | None = None

    @field_validator("type_id", "value_id", mode="before")
    def convert_id_to_uuid(cls, value):  # pylint: disable=C0116.E0213
        if value is not None and isinstance(value, str):
            return UUID(value)
        return value


class PreDefinedSubjectProperty(SubjectPropertyBase):
    """Default value is only set for type checker. Otherwise ValueError is raised later if None as
    this field is required in pre-defined subject properties"""

    value_id: UUID | str | None = None

    @field_validator("value_id", mode="before")
    def ensure_value_id_exists(cls, value):  # pylint: disable=C0116.E0213
        if value is None:
            raise ValueError("Value id cannot be empty in a PreDefinedSubjectProperty.")
        return value


class NumberSubjectProperty(NumberTypeMixin, SubjectPropertyBase): ...


class TextSubjectProperty(TextTypeMixin, SubjectPropertyBase): ...


class LocationSubjectProperty(LocationTypeMixin, SubjectPropertyBase): ...


class MapLayerSubjectProperty(MapLayerTypeMixin, SubjectPropertyBase): ...


class ImageSubjectProperty(ImageTypeMixin, SubjectPropertyBase): ...


class AreaSubjectProperty(AreaTypeMixin, SubjectPropertyBase): ...


class UnknownDataTypeSubjectProperty(UnknownTypeMixin, SubjectPropertyBase): ...


SubjectProperty: TypeAlias = (
    NumberSubjectProperty
    | TextSubjectProperty
    | LocationSubjectProperty
    | MapLayerSubjectProperty
    | ImageSubjectProperty
    | PreDefinedSubjectProperty
    | UnknownDataTypeSubjectProperty  # put last to catch any new data type
)

subject_property_adapter: TypeAdapter[SubjectProperty] = TypeAdapter(SubjectProperty)
