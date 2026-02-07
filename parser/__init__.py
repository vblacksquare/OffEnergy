
from loguru import logger

from abc import ABC, abstractmethod

from models import Schedule


class Parser(ABC):
    def __init__(self):
        self.log = logger.bind(classname=self.__class__.__name__)

    @abstractmethod
    async def get_schedule(self) -> list[Schedule]:
        pass
