
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram import types

from bot.factory import CallbackFactory

from models import User


start_router = Router()


@start_router.message(Command("start"))
async def handle_start(message: types.Message, state: FSMContext):
    await state.clear()

    user = await User.find_one(User.telegram_id == message.from_user.id)
    keyboard, msg = await get_start(user)

    await message.reply(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


@start_router.callback_query(CallbackFactory.filter(F.action == "start"))
async def handle_start_query(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    user = await User.find_one(User.telegram_id == callback.from_user.id)
    keyboard, msg = await get_start(user)

    await callback.message.edit_text(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


async def get_start(user: User) -> tuple[InlineKeyboardBuilder, str]:
    keyboard = InlineKeyboardBuilder()
    keyboard.row(

        InlineKeyboardButton(
            text=_("schedule_bt"),
            callback_data=CallbackFactory(action="schedule").pack()
        ),
        InlineKeyboardButton(
            text=_("turn_off_nots" if user.is_nots else "turn_on_nots"),
            callback_data=CallbackFactory(action="turn_nots").pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=_("city_bt"),
            callback_data=CallbackFactory(action="city").pack()
        ),
        InlineKeyboardButton(
            text=_("queue_bt"),
            callback_data=CallbackFactory(action="queue").pack()
        )
    )
    keyboard.row(
        InlineKeyboardButton(
            text=_("language_bt"),
            callback_data=CallbackFactory(action="language").pack()
        )
    )

    return keyboard, _("start_msg").format(
        city=_(user.city.value),
        queue=_(user.queue.value),
    )
