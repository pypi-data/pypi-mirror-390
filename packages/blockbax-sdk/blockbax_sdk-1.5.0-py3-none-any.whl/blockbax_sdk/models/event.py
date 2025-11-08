from typing import Literal
from uuid import UUID

from ..models.base import BlockbaxModel
from .type_hints import BlockbaxDatetime


class Event(BlockbaxModel):
    id: UUID
    event_trigger_id: UUID
    event_trigger_version: int
    event_level: Literal["OK", "INFORMATION", "WARNING", "PROBLEM"]
    subject_id: UUID
    condition_set_ids: list[UUID]
    start_date: BlockbaxDatetime
    end_date: BlockbaxDatetime | None = None
    suppressed: bool
