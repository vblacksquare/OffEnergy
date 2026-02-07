
from typing import Any

from aiogram.types import TelegramObject
from aiogram.utils.i18n import I18nMiddleware

from models import User

from config import get_config


class UserLanguageMiddleware(I18nMiddleware):
    async def get_locale(self, event: TelegramObject, data: dict[str, Any]):

        try:
            user_id = event.from_user.id

        except Exception as err:
            return get_config().telegram.languages[0]

        user = await User.find_one(User.telegram_id == user_id)

        if not user or not user.language:
            return get_config().telegram.languages[0]

        return user.language.value
