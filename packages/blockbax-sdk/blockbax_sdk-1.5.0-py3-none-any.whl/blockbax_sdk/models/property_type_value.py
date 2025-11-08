from typing_extensions import TypeAlias
from typing import Union

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


class PropertyTypeValueBase(BlockbaxModel):
    id: UUID | None = None
    caption: str | None = None
    inherit: bool | None = None

    @field_validator("id", mode="before")
    def convert_id_to_uuid(cls, value):  # pylint: disable=C0116.E0213
        if value is not None and isinstance(value, str):
            return UUID(value)
        return value


class NumberPropertyTypeValue(NumberTypeMixin, PropertyTypeValueBase): ...


class TextPropertyTypeValue(TextTypeMixin, PropertyTypeValueBase): ...


class LocationPropertyTypeValue(LocationTypeMixin, PropertyTypeValueBase): ...


class MapLayerPropertyTypeValue(MapLayerTypeMixin, PropertyTypeValueBase): ...


class ImagePropertyTypeValue(ImageTypeMixin, PropertyTypeValueBase): ...


class AreaPropertyTypeValue(AreaTypeMixin, PropertyTypeValueBase): ...


class UnknownDataTypePropertyTypeValue(UnknownTypeMixin, PropertyTypeValueBase): ...


# Unknown type should be put last to catch any new data types
# see the docs for more info  https://docs.pydantic.dev/latest/concepts/unions/
PropertyTypeValue: TypeAlias = Union[
    NumberPropertyTypeValue,
    TextPropertyTypeValue,
    LocationPropertyTypeValue,
    MapLayerPropertyTypeValue,
    ImagePropertyTypeValue,
    UnknownDataTypePropertyTypeValue,
]

property_type_value_adapter: TypeAdapter[PropertyTypeValue] = TypeAdapter(
    PropertyTypeValue
)
