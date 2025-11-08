from typing import Any, Iterable, Sequence
from uuid import UUID
from pydantic import field_validator
from .base import BlockbaxModel
from .type_hints import BlockbaxDatetime


class SubjectTypePrimaryLocation(BlockbaxModel):
    # Currently Literal["PROPERTY_TYPE", "METRIC"];
    type: str
    id: UUID

    @field_validator("id", mode="before")
    def convert_id_to_uuid(cls, value):  # pylint: disable=C0116.E0213
        if value is not None and isinstance(value, str):
            return UUID(value)
        return value


class SubjectTypePropertyType(BlockbaxModel):
    id: UUID
    required: bool
    visible: bool = True

    @field_validator("id", mode="before")
    def convert_id_to_uuid(cls, value):  # pylint: disable=C0116.E0213
        if value is not None and isinstance(value, str):
            return UUID(value)
        return value


class SubjectType(BlockbaxModel):
    id: UUID
    name: str
    created_date: BlockbaxDatetime
    updated_date: BlockbaxDatetime | None = None
    parent_subject_type_ids: list[UUID] | None = None
    primary_location: SubjectTypePrimaryLocation | None = None
    property_types: list[SubjectTypePropertyType] | None = None

    def add_property_types(
        self, property_types: Sequence[SubjectTypePropertyType | dict[str, Any]]
    ) -> None:
        """Adds new property types to its property_types attribute."""
        if not self.property_types:
            self.property_types = []
        type_safe_property_types: list[SubjectTypePropertyType] = [
            (
                property_type
                if isinstance(property_type, SubjectTypePropertyType)
                else SubjectTypePropertyType.model_validate(property_type)
            )
            for property_type in property_types
        ]
        self.property_types.extend(type_safe_property_types)

    def remove_property_types(self, property_type_ids: Sequence[UUID | str]) -> None:
        """Removes property types from its property_types attribute by Id."""
        property_type_ids = [
            (
                UUID(property_type_id)
                if isinstance(property_type_id, str)
                else property_type_id
            )
            for property_type_id in property_type_ids
        ]
        if not self.property_types:
            return
        for property_type in self.property_types:
            if property_type.id in property_type_ids:
                self.property_types.remove(property_type)

    def contains_property_type(self, property_type_id: UUID | str) -> bool:
        if self.property_types is None:
            return False
        if isinstance(property_type_id, str):
            property_type_id = UUID(property_type_id)
        return any(
            property_type_id == property_type.id
            for property_type in self.property_types
        )
