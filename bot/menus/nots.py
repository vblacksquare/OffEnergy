
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram import types

from bot.factory import CallbackFactory

from models import User

from .start import get_start


nots_router = Router()


@nots_router.message(Command("turn_nots"))
async def handle_start(message: types.Message, state: FSMContext):
    await state.clear()

    user = await User.find_one(User.telegram_id == message.from_user.id)
    user.is_nots = not user.is_nots
    await user.save()

    keyboard, msg = await get_start(user)

    await message.reply(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


@nots_router.callback_query(CallbackFactory.filter(F.action == "turn_nots"))
async def handle_start_query(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()

    user = await User.find_one(User.telegram_id == callback.from_user.id)
    user.is_nots = not user.is_nots
    await user.save()

    keyboard, msg = await get_start(user)

    await callback.message.edit_text(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )
