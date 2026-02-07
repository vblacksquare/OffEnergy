
from aiogram import Router
from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

from models import User
from enums import Language

from bot.factory import CallbackFactory

from config import get_config


new_user_router = Router()
config = get_config()


async def handle_new_user_msg(message: types.Message):
    if message.from_user.language_code in get_config().telegram.languages:
        language = Language(message.from_user.language_code)

    else:
        language = Language(get_config().telegram.languages[0])

    user = User(
        telegram_id=message.from_user.id,
        language=language,
    )
    await user.save()

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=_("skip_bt"),
            callback_data=CallbackFactory(action="city").pack()
        )
    )

    await message.reply(
        text=_("welcome_msg"),
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )


async def handle_new_user_query(callback: types.CallbackQuery):
    if callback.from_user.language_code in get_config().telegram.languages:
        language = Language(callback.from_user.language)

    else:
        language = Language(get_config().telegram.languages[0])

    user = User(
        telegram_id=callback.from_user.id,
        language=language,
    )
    await user.save()

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        InlineKeyboardButton(
            text=_("skip_bt"),
            callback_data=CallbackFactory(action="city").pack()
        )
    )

    await callback.message.edit_text(
        text=_("welcome_msg"),
        reply_markup=keyboard.as_markup(),
        parse_mode="HTML"
    )
