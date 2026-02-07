
from datetime import datetime

from . import Document
from .meta import TimestampMixin

from enums import City, Queue, ScheduleStatus, ScheduleDelivery


class Schedule(TimestampMixin, Document):
    city: City
    queue: Queue
    date: datetime
    start_at: float
    end_at: float
    delivery: ScheduleDelivery
    status: ScheduleStatus

    @property
    def cid(self):
        return "-".join([
            self.city.value,
            self.queue.value,
            self.date.strftime("%Y-%m-%dT%H:%M:%S"),
            self.time_seria,
            self.status.value
        ])

    @property
    def time_seria(self):
        return "-".join(map(str, [self.start_at, self.end_at]))
