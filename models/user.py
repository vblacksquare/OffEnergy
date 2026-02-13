
from typing import Optional

from . import Document
from .meta import TimestampMixin

from enums import City, Language, Queue


class User(TimestampMixin, Document):
    telegram_id: int
    city: Optional[City] = None
    queue: Optional[Queue] = None
    language: Optional[Language] = None
    is_nots: bool = True

    @property
    def lang(self) -> str:
        return self.language.value
