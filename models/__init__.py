
from beanie import Document
from beanie import init_beanie

from motor.motor_asyncio import AsyncIOMotorClient

from .user import User
from .schedule import Schedule


async def setup_database(uri: str, name: str):
    client = AsyncIOMotorClient(uri)[name]
    await init_beanie(client, document_models=Document.__subclasses__())
