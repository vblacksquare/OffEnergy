
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

    @property
    def start_at_date(self):
        minutes = round(int(str(self.start_at).split(".")[-1]) * 60 / 10)

        if minutes == 60:
            return self.date.replace(
                hour=round(self.start_at),
                minute=59,
                second=59,
                microsecond=59
            )

        else:
            return self.date.replace(
                hour=round(self.start_at),
                minute=minutes,
                second=10,
                microsecond=59
            )

    @property
    def end_at_date(self):
        minutes = round(int(str(self.start_at).split(".")[-1]) * 60 / 10)

        if minutes == 60:
            return self.date.replace(
                hour=round(self.end_at),
                minute=59,
                second=59,
                microsecond=59
            )

        else:
            return self.date.replace(
                hour=round(self.end_at),
                minute=minutes,
                second=10,
                microsecond=59
            )
