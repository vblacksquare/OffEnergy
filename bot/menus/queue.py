
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.utils.i18n import gettext as _
from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from models import User
from enums import Queue, City

from bot.factory import CallbackFactory
from bot.state import MainState

from config import get_config


queue_router = Router()
config = get_config()


queries = {
    City.mykolaiv: (
        2,
        [
            Queue.q1_1, Queue.q1_2,
            Queue.q2_1, Queue.q2_2,
            Queue.q3_1, Queue.q3_2,
            Queue.q4_1, Queue.q4_2,
            Queue.q5_1, Queue.q5_2,
            Queue.q6_1, Queue.q6_2,
        ]
    )
}


@queue_router.callback_query(CallbackFactory.filter(F.action == "queue"))
async def handle_queue_query(callback: CallbackQuery, state: FSMContext):
    user = await User.find_one(User.telegram_id == callback.from_user.id)
    keyboard, msg = await get_queue(user, state)

    await callback.message.edit_text(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )


@queue_router.message(Command("queue"))
async def handle_queue_msg(message: Message, state: FSMContext):
    user = await User.find_one(User.telegram_id == message.from_user.id)
    keyboard, msg = await get_queue(user, state)

    await message.reply(
        msg,
        reply_markup=keyboard.as_markup(),
        parse_mode="html"
    )



@queue_router.callback_query(CallbackFactory.filter(F.action == "change_queue"))
async def change_queue(callback: CallbackQuery, callback_data: CallbackFactory, state: FSMContext):
    queue = Queue(callback_data.value)

    user = await User.find_one(User.telegram_id == callback.from_user.id)
    if queue == user.queue:
        return

    user.queue = queue
    await user.save()

    await handle_queue_query(callback, state)


async def get_queue(user: User, state: FSMContext) -> tuple[InlineKeyboardBuilder, str]:
    keyboard = InlineKeyboardBuilder()

    col, current_queries = queries[user.city]
    for i in range(0, len(current_queries), col):
        keyboard.row(*[
            InlineKeyboardButton(
                text=_(queue),
                callback_data=CallbackFactory(action="change_queue", value=queue).pack()
            )
            for queue in current_queries[i:i+col]
        ])

    current_state = await state.get_state()
    if user.queue:
        current_queue = _(user.queue.value)

        if current_state == MainState.new_user:
            keyboard.row(
                InlineKeyboardButton(
                    text=_("skip_bt"),
                    callback_data=CallbackFactory(action="start").pack()
                )
            )
            await state.clear()

        else:
            keyboard.row(
                InlineKeyboardButton(
                    text=_("back_bt"),
                    callback_data=CallbackFactory(action="start").pack()
                )
            )

    else:
        current_queue = _("no_queue")

    return keyboard, _("queue_msg").format(queue=current_queue)
