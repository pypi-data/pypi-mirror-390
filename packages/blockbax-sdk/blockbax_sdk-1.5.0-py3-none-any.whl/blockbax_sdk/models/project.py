from uuid import UUID
from .base import BlockbaxModel
from .type_hints import BlockbaxDatetime
from . import Subject, Metric, SubjectType, PropertyType


class Project(BlockbaxModel):
    id: UUID
    created_date: BlockbaxDatetime
    name: str
    description: str
    timezone_id: str
    organization_id: UUID
    updated_date: BlockbaxDatetime | None = None


class ProjectResources(BlockbaxModel):
    project: Project
    subjects: list[Subject]
    metrics: list[Metric]
    subject_types: list[SubjectType]
    property_types: list[PropertyType]
