
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram import types

from bot.factory import CallbackFactory

from models import User, Schedule

from utils.convert import to_hours, from_hours


schedule_router = Router()


@schedule_router.callback_query(CallbackFactory.filter(F.action == "schedule"))
async def handle_start_query(callback: types.CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    await state.clear()

    user = await User.find_one(User.telegram_id == callback.from_user.id)
    keyboard, msg = await get_schedule(user, callback_data.value)

    await callback.message.edit_text(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


@schedule_router.message(Command("schedule"))
async def handle_start(message: types.Message, state: FSMContext):
    await state.clear()

    user = await User.find_one(User.telegram_id == message.from_user.id)
    keyboard, msg = await get_schedule(user)

    await message.reply(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


async def get_schedule(user: User, value: str = None) -> tuple[InlineKeyboardBuilder, str]:
    value = 0 if value is None else int(value)

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=_("yesterday"),
            callback_data=CallbackFactory(action="schedule", value="-1").pack()
        ),
        InlineKeyboardButton(
            text=_("today"),
            callback_data=CallbackFactory(action="schedule").pack()
        ),
        InlineKeyboardButton(
            text=_("tomorrow"),
            callback_data=CallbackFactory(action="schedule", value="1").pack()
        ),
    )
    keyboard.row(
        InlineKeyboardButton(
            text=_("back_bt"),
            callback_data=CallbackFactory(action="start").pack()
        )
    )

    now = datetime.now()
    start = (now + timedelta(days=value)).replace(hour=0, minute=0, second=0, microsecond=0)
    end = start.replace(hour=23, minute=59, second=59, microsecond=0)

    docs = await Schedule.find(
        Schedule.date > start,
        Schedule.date <= end,
        Schedule.queue == user.queue,
        Schedule.city == user.city
    ).to_list()

    if docs:
        docs = sorted(docs, key=lambda x: x.start_at)

        joined = []
        current_doc = docs[0]

        for doc in docs[1:]:
            if doc.status == current_doc.status:
                current_doc.end_at = doc.end_at

            else:
                joined.append(current_doc)
                current_doc = doc

        joined.append(current_doc)

        parts = []
        hours_now = from_hours(now)

        for doc in joined:
            parts.append(
                _("current_row" if doc.start_at <= hours_now <= doc.end_at else "row").format(
                    start_at=to_hours(doc.start_at),
                    end_at=to_hours(doc.end_at),
                    status=_(doc.status.value),
                )
            )

        schedule = ''.join(parts)

    else:
        schedule = _("no_schedule")

    return keyboard, _("schedule_msg").format(
        city=_(user.city.value),
        queue=_(user.queue.value),
        day=end.strftime("%d.%m.%Y"),
        schedule=schedule
    )
