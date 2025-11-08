from uuid import UUID
from ..models.base import BlockbaxModel
from .type_hints import (
    BlockbaxDatetime,
)


class Metric(BlockbaxModel):
    id: UUID
    created_date: BlockbaxDatetime
    subject_type_id: UUID
    name: str
    # Usually Literal["NUMBER", "TEXT", "LOCATION"]; relaxed type for cases with new unknown data types
    data_type: str
    # Usually Literal["INGESTED", "CALCULATED", "SIMULATED"]; relaxed type for cases with new unknown data types
    type: str
    updated_date: BlockbaxDatetime | None = None
    unit: str | None = None
    precision: int | None = None
    visible: bool | None = None
    discrete: bool | None = None
    preferred_color: str | None = None
    external_id: str | None = None
    # Usually Literal["OWN", "CHILD"]; relaxed type for cases with new mapping levels
    mapping_level: str | None = None
