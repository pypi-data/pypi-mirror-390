from typing import TypedDict
from .base import BlockbaxModel
from .measurement import Measurement


class Ingestion(BlockbaxModel):
    ingestion_id: str
    measurement: Measurement


class IngestionCollection(BlockbaxModel):
    ingestion_id: str
    measurements: list[Measurement]


class IngestedSeries(BlockbaxModel):
    series: list[IngestionCollection]


class IngestionIdOverride(TypedDict):
    metric_id: str
