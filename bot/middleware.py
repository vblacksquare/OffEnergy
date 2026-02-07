
from aiogram import BaseMiddleware, Dispatcher, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from models import User
from config import get_config

from bot.state import MainState

from .menus.new_user import handle_new_user_msg, handle_new_user_query
from .menus.queue import handle_queue_msg, handle_queue_query
from .menus.city import handle_city_msg, handle_city_query


class ClearFsmMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot, dispatcher: Dispatcher):
        super().__init__()

        self.bot = bot
        self.dp = dispatcher

    async def __call__(self, handler, event: Message, data: dict):
        state: FSMContext = data.get("state")

        if event.text and event.text.lower() in get_config().telegram.commands and await state.get_state():
            await state.clear()
            return await self.dp._process_update(bot=self.bot, update=data['event_update'])

        return await handler(event, data)


class NewUserMiddlewareMsg(BaseMiddleware):
    async def __call__(self, handler, event: Message, data: dict):
        telegram_user = data.get("event_from_user")
        user = await User.find_one(User.telegram_id == telegram_user.id)

        state: FSMContext = data.get("state")

        if not user:
            await state.set_state(MainState.new_user)
            await handle_new_user_msg(event)

        elif not user.city:
            await state.set_state(MainState.new_user)
            await handle_city_msg(event, state)

        elif not user.queue:
            await state.set_state(MainState.new_user)
            await handle_queue_msg(event, state)

        else:
            await handler(event, data)


class NewUserMiddlewareQuery(BaseMiddleware):
    async def __call__(self, handler, event: CallbackQuery, data: dict):
        telegram_user = data.get("event_from_user")
        user = await User.find_one(User.telegram_id == telegram_user.id)

        state: FSMContext = data.get("state")

        if not user:
            await state.set_state(MainState.new_user)
            await handle_new_user_query(event)

        elif not user.city:
            if "change_city" in event.data:
                await handler(event, data)

            else:
                await state.set_state(MainState.new_user)
                await handle_city_query(event, state)

        elif not user.queue:
            if "change_queue" in event.data:
                await handler(event, data)

            else:
                await state.set_state(MainState.new_user)
                await handle_queue_query(event, state)

        else:
            await handler(event, data)
