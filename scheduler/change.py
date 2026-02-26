
from typing import Optional
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram.utils.keyboard import InlineKeyboardBuilder,InlineKeyboardButton

from bot import i18n, bot
from enums import City, Queue
from models import Schedule, Change, User
from bot.menus.schedule import get_schedule
from bot.factory import CallbackFactory

from utils.convert import join_schedule


async def update_pusher():
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

    schedule: dict[str, Optional[Schedule]] = {}
    new_schedule: dict[str, Optional[Schedule]] = {}

    old_changes: list[Change] = await Change.find(
        Schedule.date > start,
        Schedule.date <= end,
        Schedule.city == city,
        Schedule.queue == queue
    ).to_list()
    old_changes_ids = [change.schedule_id for change in old_changes]

    changes = []
    for doc in docs:
        if doc.time_seria not in schedule:
            schedule[doc.time_seria] = None

        old_doc = schedule[doc.time_seria]
        if old_doc is None:
            schedule[doc.time_seria] = doc

        elif old_doc.created_at < doc.created_at:
            if doc.id in old_changes_ids:
                schedule[doc.time_seria] = doc

            else:
                new_schedule = schedule.copy()
                new_schedule[doc.time_seria] = doc
                changes.append(Change(
                    schedule_id=doc.id,
                    city=doc.city,
                    queue=doc.queue,
                    date=doc.date,
                    start_at=doc.start_at,
                    end_at=doc.end_at,
                    status=doc.status,
                ))

    if len(changes) > 0:
        await Change.insert_many(changes)

        part_schedule = []
        new_part_schedule = []

        for change in changes:
            part_schedule.append(schedule[change.time_seria])
            new_part_schedule.append(new_schedule[change.time_seria])

        for user in users:
            old_schedule = join_schedule(part_schedule, now, user.lang)
            new_schedule = join_schedule(new_part_schedule, now, user.lang)

            keyboard = InlineKeyboardBuilder()
            keyboard.row(
                InlineKeyboardButton(
                    text=i18n.gettext("yesterday", locale=user.lang),
                    callback_data=CallbackFactory(action="schedule", value="-1").pack()
                ),
                InlineKeyboardButton(
                    text=i18n.gettext("today", locale=user.lang),
                    callback_data=CallbackFactory(action="schedule").pack()
                ),
                InlineKeyboardButton(
                    text=i18n.gettext("tomorrow", locale=user.lang),
                    callback_data=CallbackFactory(action="schedule", value="1").pack()
                ),
            )
            keyboard.row(
                InlineKeyboardButton(
                    text=i18n.gettext("back_bt", locale=user.lang),
                    callback_data=CallbackFactory(action="start").pack()
                )
            )
            schedule = join_schedule(docs, now, user.lang)

            await bot.send_message(
                text=i18n.gettext("update_schedule_msg", locale=user.lang).format(
                    city=i18n.gettext(user.city.value, locale=user.lang),
                    queue=i18n.gettext(user.queue.value, locale=user.lang),
                    day=end.strftime("%d.%m.%Y"),
                    schedule=schedule
                ),
                reply_markup=keyboard.as_markup(),
                parse_mode="html",
                chat_id=user.telegram_id
            )
