
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from enums import Language
from models import User

from bot.factory import CallbackFactory

from config import get_config


language_router = Router()


@language_router.callback_query(CallbackFactory.filter(F.action == "language"))
async def handle_language_query(callback: CallbackQuery = None, user_message: Message = None, action: str = "return"):
    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        *[
            InlineKeyboardButton(
                text=_(language),
                callback_data=CallbackFactory(action="change_language", value=f"{action}|{language}").pack()
            )
            for language in get_config().telegram.languages
        ]
    )
    keyboard.row(
        InlineKeyboardButton(
            text=_("skip_bt") if action == "skip" else _("back_bt"),
            callback_data=CallbackFactory(action="start").pack()
        )
    )

    if user_message:
        await user_message.answer(
            _("language_msg"),
            reply_markup=keyboard.as_markup(),
            parse_mode="html"
        )

    else:
        if callback.message.photo:
            await callback.message.delete()
            await callback.message.answer(
                _("language_msg"),
                reply_markup=keyboard.as_markup(),
                parse_mode="html"
            )

        else:
            await callback.message.edit_text(
                _("language_msg"),
                reply_markup=keyboard.as_markup(),
                parse_mode="html"
            )


@language_router.message(Command("language"))
async def handle_language(message: Message):
    action = "return"

    keyboard = InlineKeyboardBuilder()
    keyboard.row(
        *[
            InlineKeyboardButton(
                text=_(language),
                callback_data=CallbackFactory(action="change_language", value=f"{action}|{language}").pack()
            )
            for language in get_config().telegram.languages
        ]
    )
    keyboard.row(
        InlineKeyboardButton(
            text=_("skip_bt") if action == "skip" else _("back_bt"),
            callback_data=CallbackFactory(action="start").pack()
        )
    )

    await message.reply(
        _("language_msg"),
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


@language_router.callback_query(CallbackFactory.filter(F.action == "change_language"))
async def hange_language_change(callback: CallbackQuery, callback_data: CallbackFactory, i18n):
    action, language = callback_data.value.split("|")
    language = Language(language)

    i18n.ctx_locale.set(language.value)
    user = await User.find_one(User.telegram_id == callback.from_user.id)

    if user.language == language:
        return

    user.language = language
    await user.save()
    await handle_language_query(callback, action=action)
