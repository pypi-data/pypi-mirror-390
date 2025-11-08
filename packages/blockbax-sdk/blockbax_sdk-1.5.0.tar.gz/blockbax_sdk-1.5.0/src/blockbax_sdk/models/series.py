from uuid import UUID
from .base import BlockbaxModel

from .measurement import Measurement

import datetime


class Series(BlockbaxModel):
    subject_id: UUID
    metric_id: UUID
    measurements: list[Measurement]

    def __iter__(self):
        return iter(self.measurements)

    @property
    def latest_date(self) -> datetime.datetime:
        latest_date = 0
        for measurement in self.measurements:
            if measurement.date is not None:
                latest_date = (
                    measurement.date if measurement.date > latest_date else latest_date
                )
        return datetime.datetime.fromtimestamp(latest_date / 1000.0)
