
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from models import User
from enums import City

from bot.factory import CallbackFactory
from bot.state import MainState

from config import get_config


city_router = Router()
config = get_config()


@city_router.callback_query(CallbackFactory.filter(F.action == "city"))
async def handle_city_query(callback: CallbackQuery, state: FSMContext):
    user = await User.find_one(User.telegram_id == callback.from_user.id)
    keyboard, msg = await get_city(user, state)

    await callback.message.edit_text(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


@city_router.callback_query(Command("city"))
async def handle_city_msg(message: Message, state: FSMContext):
    user = await User.find_one(User.telegram_id == message.from_user.id)
    keyboard, msg = await get_city(user, state)

    await message.reply(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


@city_router.callback_query(CallbackFactory.filter(F.action == "change_city"))
async def change_city(callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    city = City(callback_data.value)

    user = await User.find_one(User.telegram_id == callback.from_user.id)
    if city == user.city:
        return

    user.city = city
    user.queue = None
    await user.save()

    await state.set_state(MainState.new_user)
    await handle_city_query(callback, state)


async def get_city(user: User, state: FSMContext) -> tuple[InlineKeyboardBuilder, str]:
    keyboard = InlineKeyboardBuilder()

    col = 2
    for i in range(0, len(config.telegram.cities), col):
        keyboard.row(*[
            InlineKeyboardButton(
                text=_(city),
                callback_data=CallbackFactory(action="change_city", value=city).pack()
            )
            for city in config.telegram.cities[i:i + col]
        ])

    current_state = await state.get_state()
    if user.city:
        current_city = _(user.city.value)

        if current_state == MainState.new_user:
            keyboard.row(
                InlineKeyboardButton(
                    text=_("skip_bt"),
                    callback_data=CallbackFactory(action="start").pack()
                )
            )

        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=_("back_bt"),
                    callback_data=CallbackFactory(action="start").pack()
                )
            )

    else:
        current_city = _("no_city")

    return keyboard, _("city_msg").format(city=current_city)
