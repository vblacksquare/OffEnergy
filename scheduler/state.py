from typing import Optional
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import bot, i18n
from bot.factory import CallbackFactory

from enums import City, Queue, ScheduleStatus
from models import Schedule, User

from utils.convert import from_hours, get_joined_schedule, to_time_left


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

    hours_now = from_hours(now)
    joined = get_joined_schedule(docs)

    current_schedule: Optional[Schedule] = None
    i = 0

    for i, doc in enumerate(joined):
        if doc.start_at <= hours_now <= doc.end_at:
            current_schedule = doc
            break

    if current_schedule is None:
        current_schedule = joined[-1]

    parts = joined[i+1:i+3]

    for user in users:
        msg = None

        if len(parts) == 0:
            diff = to_time_left(
                round(
                    abs(now.timestamp() - (start + timedelta(days=1)).timestamp()) / 3600, 2
                ),
                user.lang
            )

            msg = i18n.gettext("push_change", locale=user.lang).format(
                start=str(diff),
                meta=""
            )

        elif len(parts) == 1:
            upcoming_schedule = parts[0]

            diff = to_time_left(
                round(
                    abs(now.timestamp() - upcoming_schedule.start_at_date.timestamp()) / 3600, 2
                ),
                user.lang
            )

            if upcoming_schedule.status == ScheduleStatus.on:
                msg = i18n.gettext("push_on", locale=user.lang).format(
                    start=str(diff),
                    meta=i18n.gettext("next_timetable", locale=user.lang)
                )

            elif upcoming_schedule.status == ScheduleStatus.off:
                msg = i18n.gettext("push_off", locale=user.lang).format(
                    start=str(diff),
                    meta=i18n.gettext("next_timetable", locale=user.lang)
                )

            elif upcoming_schedule.status == ScheduleStatus.probably:
                status = "on" if current_schedule.status == ScheduleStatus.off else "off"

                msg = i18n.gettext(f"push_probably_{status}").format(
                    start=str(diff),
                    meta=i18n.gettext("next_timetable", locale=user.lang)
                )

        elif len(parts) == 2:
            upcoming_schedule = parts[0]
            next_schedule = parts[1]

            diff = to_time_left(
                round(
                    abs(now.timestamp() - upcoming_schedule.start_at_date.timestamp()) / 3600, 2
                ),
                user.lang
            )
            diff1 = to_time_left(
                round(
                    abs(now.timestamp() - next_schedule.start_at_date.timestamp()) / 3600, 2
                ),
                user.lang
            )

            if upcoming_schedule.status == ScheduleStatus.on:
                msg = i18n.gettext("push_on", locale=user.lang).format(
                    start=str(diff),
                    meta=""
                )

            elif upcoming_schedule.status == ScheduleStatus.off:
                msg = i18n.gettext("push_off", locale=user.lang).format(
                    start=str(diff),
                    meta=""
                )

            elif upcoming_schedule.status == ScheduleStatus.probably:
                if next_schedule.status == ScheduleStatus.on:
                    msg = i18n.gettext("push_combined_on", locale=user.lang).format(
                        start=str(diff),
                        end=str(diff1),
                        meta=""
                    )

                elif next_schedule.status == ScheduleStatus.off:
                    msg = i18n.gettext("push_combined_off", locale=user.lang).format(
                        start=str(diff),
                        end=str(diff1),
                        meta=""
                    )

        if msg is None:
            continue

        keyboard = InlineKeyboardBuilder()
        keyboard.row(
            InlineKeyboardButton(
                text=i18n.gettext("full_schedule_bt", locale=user.lang),
                callback_data=CallbackFactory(action="schedule")
            )
        )

        await bot.send_message(
            text=msg,
            parse_mode="HTML",
            chat_id=user.telegram_id
        )
