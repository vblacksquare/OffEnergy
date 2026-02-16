
from loguru import logger

from aiogram import Dispatcher, Bot
from aiogram.utils.i18n import I18n
from aiogram.fsm.storage.mongo import MongoStorage
from aiogram.utils.callback_answer import CallbackAnswerMiddleware

from .i18n_middleware import UserLanguageMiddleware
from .middleware import ClearFsmMiddleware, NewUserMiddlewareMsg, NewUserMiddlewareQuery

from config import get_config


bot = Bot(token=get_config().telegram.bot_token)

i18n = I18n(path=get_config().resources.locales_path, default_locale="ru", domain="messages")


async def run_telegram():
    try:
        from .menus import root_router

        dp = Dispatcher(storage=MongoStorage.from_url(get_config().database.uri))
        dp.include_router(root_router)

        dp.message.middleware(ClearFsmMiddleware(bot, dp))
        dp.message.middleware(NewUserMiddlewareMsg())
        dp.callback_query.middleware(NewUserMiddlewareQuery())
        dp.callback_query.middleware(CallbackAnswerMiddleware())

        i18n_middleware = UserLanguageMiddleware(i18n)
        i18n_middleware.setup(dp)

        bot.username = (await bot.get_me()).username

        await dp.start_polling(bot, i18n=i18n)

    except Exception as err:
        logger.exception(err)
