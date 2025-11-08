from __future__ import annotations
from decimal import Decimal
from typing import Any, Literal
from uuid import UUID

from pydantic import ConfigDict, field_validator, model_validator

from ..models.base import BlockbaxModel
from .type_hints import (
    BlockbaxDatetime,
)

from .data_types import Location, Area


class Period(BlockbaxModel):
    unit: Literal["MILLISECOND", "SECOND", "MINUTE", "HOUR", "DAY", "WEEK"]
    amount: int

    @field_validator("amount", mode="before")
    def validate_amount(cls, value):  # pylint: disable=C0116.E0213
        if value < 1:
            raise ValueError(
                "Period amount. Total should be a max of 1 week in whichever period unit."
            )
        return value


class Aggregation(BlockbaxModel):
    function: Literal["MIN", "MAX", "SUM", "COUNT", "AVG"]
    period: Period


class Offset(BlockbaxModel):
    type: Literal["PREVIOUS_VALUE", "PERIOD"]
    period: Period | None = None

    @model_validator(mode="after")
    def validate_offset(self):  # pylint: disable=C0116.E0213
        if self.type == "PERIOD" and self.period is None:
            raise ValueError("Period is required when type is PERIOD.")
        return self


class Operand(BlockbaxModel):
    type: Literal[
        "METRIC", "PROPERTY_TYPE", "STATIC_VALUE", "VALUE_CHANGE", "CALCULATION"
    ]
    id: UUID | str | None = None
    number: int | float | Decimal | str | None = None
    text: str | None = None
    location: Location | None = None
    area: Area | None = None
    aggregation: Aggregation | None = None
    left_operand: Operand | None = None
    arithmetic_operator: (
        Literal[
            "ADDITION",
            "MULTIPLICATION",
            "DIVISION",
            "DISTANCE",
            "DIFFERENCE",
            "ABSOLUTE_DIFFERENCE",
            "PERCENTAGE_DIFFERENCE",
            "ABSOLUTE_PERCENTAGE_DIFFERENCE",
        ]
        | None
    ) = None
    right_operand: Operand | None = None
    offset: Offset | None = None

    @model_validator(mode="after")
    def validate_value_change_operand(self):  # pylint: disable=C0116.E0213
        if self.type == "VALUE_CHANGE":
            if self.arithmetic_operator not in [
                "DIFFERENCE",
                "ABSOLUTE_DIFFERENCE",
                "PERCENTAGE_DIFFERENCE",
                "ABSOLUTE_PERCENTAGE_DIFFERENCE",
            ]:
                raise ValueError(
                    "Invalid arithmetic operator for VALUE_CHANGE operand."
                )
            # TODO is it wrongly mentioned in the docs?
            # if values.offset is None:
            #     raise ValueError("Offset must be provided for VALUE_CHANGE operand.")
        return self


Operand.model_rebuild()


class InputCondition(BlockbaxModel):
    type: Literal["THRESHOLD", "TEXT_MATCH", "GEOFENCE"]
    left_operand: Operand
    comparison_operator: Literal[
        "LESS_THAN",
        "LESS_THAN_OR_EQUALS",
        "EQUALS",
        "NOT_EQUALS",
        "GREATER_THAN_OR_EQUALS",
        "GREATER_THAN",
        "CONTAINS",
        "NOT_CONTAINS",
        "STARTS_WITH",
        "NOT_STARTS_WITH",
        "ENDS_WITH",
        "NOT_ENDS_WITH",
        "MATCHES_REGEX",
        "NOT_MATCHES_REGEX",
    ]
    right_operand: Operand

    @model_validator(mode="after")
    def validate_comparison_operator(self):
        allowed_operators = {
            "THRESHOLD": [
                "LESS_THAN",
                "LESS_THAN_OR_EQUALS",
                "EQUALS",
                "NOT_EQUALS",
                "GREATER_THAN_OR_EQUALS",
                "GREATER_THAN",
            ],
            "TEXT_MATCH": [
                "EQUALS",
                "NOT_EQUALS",
                "CONTAINS",
                "NOT_CONTAINS",
                "STARTS_WITH",
                "NOT_STARTS_WITH",
                "ENDS_WITH",
                "NOT_ENDS_WITH",
                "MATCHES_REGEX",
                "NOT_MATCHES_REGEX",
            ],
            "GEOFENCE": ["CONTAINS", "NOT_CONTAINS"],
        }
        if self.type in allowed_operators:
            if self.comparison_operator not in allowed_operators[self.type]:
                raise ValueError(
                    f"Invalid comparison operator for {type} condition: {self.comparison_operator}"
                )
        return self


class DurationCondition(BlockbaxModel):
    period: Period


class OccurrenceCondition(BlockbaxModel):
    period: Period
    occurrences: int


class DayTimeConditionRange(BlockbaxModel):
    from_time: str
    to_time: str


def override_datetime_condition_model_config() -> ConfigDict:
    """
    The day names in day time input condition should be capitalized; however the default conversion
    of camelCase to snail_case and back results a lower case string.
    Returns:
        dict: New config with upper case alias generator
    """
    override_model_config = BlockbaxModel.model_config.copy()
    override_model_config["alias_generator"] = str.upper
    return override_model_config


class DayTimeCondition(BlockbaxModel):
    # # Inherit parent model_config and override alias_generator
    model_config = ConfigDict(**override_datetime_condition_model_config())

    MONDAY: list[DayTimeConditionRange] | None = None
    TUESDAY: list[DayTimeConditionRange] | None = None
    WEDNESDAY: list[DayTimeConditionRange] | None = None
    THURSDAY: list[DayTimeConditionRange] | None = None
    FRIDAY: list[DayTimeConditionRange] | None = None
    SATURDAY: list[DayTimeConditionRange] | None = None
    SUNDAY: list[DayTimeConditionRange] | None = None

    def to_request(self) -> dict[str, Any]:
        return self.model_dump(by_alias=True, exclude_none=True, mode="json")


class ConditionSet(BlockbaxModel):
    id: UUID | str | None = None
    description: str
    input_conditions: list[InputCondition]
    duration_condition: DurationCondition | None = None
    occurrence_condition: OccurrenceCondition | None = None
    day_time_condition: DayTimeCondition | None = None

    @field_validator("id", mode="before")
    def convert_id_to_uuid(cls, value):  # pylint: disable=C0116.E0213
        if value is not None and isinstance(value, str):
            return UUID(value)
        return value


class SubjectPropertyValuesFilter(BlockbaxModel):
    type_id: UUID | str
    value_ids: list[UUID | str]


class SubjectFilterItem(BlockbaxModel):
    subject_ids: list[UUID | str] | None = None
    property_values: list[SubjectPropertyValuesFilter] | None = None


class SubjectFilter(BlockbaxModel):
    include: SubjectFilterItem | None = None
    exclude: SubjectFilterItem | None = None


class EventRule(BlockbaxModel):
    event_level: Literal["OK", "INFORMATION", "WARNING", "PROBLEM"]
    condition_sets: list[ConditionSet]


class EventTrigger(BlockbaxModel):
    id: UUID
    created_date: BlockbaxDatetime
    subject_type_id: UUID
    name: str
    version: int
    active: bool
    evaluation_trigger: Literal["INPUT_METRICS", "SUBJECT_METRICS"]
    evaluation_constraint: Literal["NONE", "ALL_TIMESTAMPS_MATCH"]
    event_rules: list[EventRule]
    updated_date: BlockbaxDatetime | None = None
    subject_filter: SubjectFilter | None = None

    class Config:
        populate_by_name = True
