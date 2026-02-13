
from loguru import logger

from datetime import datetime

from models import Schedule
from enums import City

from parser.mykolaiv import MykolaivParser


async def update_mykolaiv():
    parser = MykolaivParser()
    schedules = await parser.get_schedule()

    days: list[datetime] = []
    for schedule in schedules:
        if schedule.date not in days:
            days.append(schedule.date)

    old_schedules = []
    for day in days:
        start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        end = day

        raw_old_schedules = Schedule.find(
            Schedule.city == City.mykolaiv,
            Schedule.date > start,
            Schedule.date <= end,
        )

        async for schedule in raw_old_schedules:
            old_schedules.append(schedule.cid)

    to_add = []
    for schedule in schedules:
        if schedule.cid not in old_schedules:
            to_add.append(schedule)
    
    if len(to_add) > 0:
        logger.info(f"Adding {len(to_add)} new schedules")
        await Schedule.insert_many(to_add)

