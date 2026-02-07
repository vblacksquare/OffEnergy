
from aiogram import Router
from aiogram.utils.i18n import gettext as _
from aiogram import types


utils_router = Router()


@utils_router.message()
async def handle_start(message: types.Message):
    await message.reply(
        _("no_such_command"),
        parse_mode="HTML"
    )
