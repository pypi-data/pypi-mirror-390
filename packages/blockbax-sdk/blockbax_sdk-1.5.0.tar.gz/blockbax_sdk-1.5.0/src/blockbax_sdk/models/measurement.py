from datetime import datetime
from typing import Union

from pydantic import TypeAdapter, field_validator


from .base import BlockbaxModel
from ..util import conversions
from .data_types import (
    NumberTypeMixin,
    TextTypeMixin,
    LocationTypeMixin,
    UnknownTypeMixin,
)


class MeasurementBase(BlockbaxModel):
    date: int | float | datetime | str | None = None

    @field_validator("date")
    def convert_to_epoch_ms(cls, date):
        return conversions.convert_any_date_to_unix_millis(date=date)


class NumberMeasurement(NumberTypeMixin, MeasurementBase): ...


class LocationMeasurement(LocationTypeMixin, MeasurementBase): ...


class TextMeasurement(TextTypeMixin, MeasurementBase): ...


class UnknownMeasurement(UnknownTypeMixin, MeasurementBase): ...


# Unknown type should be put last to catch any new data types
# see the docs for more info  https://docs.pydantic.dev/latest/concepts/unions/
Measurement = Union[
    NumberMeasurement,
    LocationMeasurement,
    TextMeasurement,
    UnknownMeasurement,
]

measurement_adapter: TypeAdapter[Measurement] = TypeAdapter(Measurement)
measurements_adapter: TypeAdapter[list[Measurement]] = TypeAdapter(list[Measurement])
