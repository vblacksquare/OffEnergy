from typing import Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from bot import bot, i18n

from enums import City, Queue, ScheduleStatus
from models import Schedule, Change, User

from utils.convert import to_hours, from_hours, get_joined_schedule


async def update_state():
    now = datetime.now(ZoneInfo("Europe/Kyiv")).replace(tzinfo=None)
    start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(hour=23, minute=59, second=59, microsecond=0)

    docs = await Schedule.find(
        Schedule.date > start,
        Schedule.date <= end
    ).to_list()

    by_city = {}
    for doc in docs:
        if doc.city not in by_city:
            by_city[doc.city] = []

        by_city[doc.city].append(doc)

    for city in by_city:
        await update_by_city(now, start, end, city, by_city[city])


async def update_by_city(
    now: datetime,
    start: datetime,
    end: datetime,
    city: City,
    docs: list[Schedule]
):

    by_queue = {}
    for doc in docs:
        if doc.queue not in by_queue:
            by_queue[doc.queue] = []

        by_queue[doc.queue].append(doc)

    for queue in by_queue:
        if queue != Queue.q4_2:
            continue

        await update_by_queue(now, start, end, city, queue, by_queue[queue])


async def update_by_queue(
    now: datetime,
    start: datetime,
    end: datetime,
    city: City,
    queue: Queue,
    docs: list[Schedule]
):

    users = await User.find(
        User.city == city,
        User.queue == queue,
    ).to_list()

    hours_now = from_hours(now - timedelta(minutes=15))
    joined = get_joined_schedule(docs)

    current_schedule: Optional[Schedule] = None
    i = 0

    for i, doc in enumerate(joined):
        if doc.start_at < hours_now <= doc.end_at:
            current_schedule = doc
            break

    if not current_schedule:
        return

    parts = joined[i+1:i+3]
    if len(parts) == 0:
        print("хз там следующий график")

    elif len(parts) == 1:
        print("знаю некст но там следующий график")
        upcoming_schedule = parts[0]

        if upcoming_schedule.status == ScheduleStatus.on:
            pass

        elif upcoming_schedule.status == ScheduleStatus.off:
            pass

        elif upcoming_schedule.status == ScheduleStatus.probably:
            pass

    elif len(parts) == 2:
        print("знаю некст+некст")
