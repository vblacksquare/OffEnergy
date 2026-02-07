
import aiohttp
import json
from datetime import datetime

from . import Parser
from models import Schedule

from enums import City, Queue, ScheduleDelivery, ScheduleStatus

from utils.convert import from_hours


convert_status = {
    "OFF": ScheduleStatus.off,
    "PROBABLY_OFF": ScheduleStatus.probably,
    "SURE_OFF": ScheduleStatus.emergency
}

convert_queue = {
    "1.1": Queue.q1_1,
    "1.2": Queue.q1_2,
    "2.1": Queue.q2_1,
    "2.2": Queue.q2_2,
    "3.1": Queue.q3_1,
    "3.2": Queue.q3_2,
    "4.1": Queue.q4_1,
    "4.2": Queue.q4_2,
    "5.1": Queue.q5_1,
    "5.2": Queue.q5_2,
    "6.1": Queue.q6_1,
    "6.2": Queue.q6_2,
}


class MykolaivParser(Parser):
    async def get_schedule(self) -> list[Schedule]:
        schedules = []

        async with (aiohttp.ClientSession() as session):
            time_series = {}
            queues = {}

            async with session.get(
                url="https://off.energy.mk.ua/api/schedule/time-series"
            ) as resp:
                self.log.info(resp)

                data = await resp.json()
                for time_seria in data:
                    time_series.update({
                        time_seria["id"]: [
                            from_hours(time_seria["start"]),
                            from_hours(time_seria["end"]),
                        ]
                    })

            async with session.get(
                url="https://off.energy.mk.ua/api/outage-queue/by-type/3"
            ) as resp:
                self.log.info(resp)

                data = await resp.json()
                for queue in data:
                    queues.update({
                        queue["id"]: convert_queue[queue["name"]]
                    })

            async with session.get(
                url="https://off.energy.mk.ua/api/v2/schedule/active"
            ) as resp:
                self.log.info(resp)

                data = await resp.json()

                for day in data:
                    _queues = {}

                    date = datetime.\
                        fromisoformat(day["to"].replace("Z", "+00:00")).\
                        replace(hour=23, minute=59, second=59, microsecond=0)

                    for seria in day["series"]:
                        queue = queues[seria["outage_queue_id"]]
                        start_at, end_at = time_series[seria["time_series_id"]]
                        status = convert_status[seria["type"]]

                        schedule = Schedule(
                            city=City.mykolaiv,
                            queue=queue,
                            date=date,
                            start_at=start_at,
                            end_at=end_at,
                            delivery=ScheduleDelivery.received,
                            status=status
                        )

                        if schedule.queue not in _queues:
                            _queues[schedule.queue] = {
                                '-'.join(map(str, time_seria)): None
                                for time_seria in list(time_series.values())
                            }

                        _queues[schedule.queue][schedule.time_seria] = schedule
                        schedules.append(schedule)

                    for queue_key in _queues:
                        queue = _queues[queue_key]

                        for time_seria in queue:
                            start_at, end_at = map(float, time_seria.split("-"))

                            if queue[time_seria] is None:
                                schedule = Schedule(
                                    city=City.mykolaiv,
                                    queue=queue_key,
                                    date=date,
                                    start_at=start_at,
                                    end_at=end_at,
                                    delivery=ScheduleDelivery.received,
                                    status=ScheduleStatus.on
                                )
                                schedules.append(schedule)

        return schedules
