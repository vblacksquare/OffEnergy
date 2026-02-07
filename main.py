
import asyncio

from bot import run_telegram
from scheduler import run_cheduler
from models import setup_database

from utils.logger import setup_logger

from config import get_config


async def main():
    config = get_config()

    setup_logger(config.logger.path, config.logger.level)

    await setup_database(config.database.uri, config.database.name)

    await run_cheduler()
    await run_telegram()


if __name__ == '__main__':
    loop = asyncio.new_event_loop()
    loop.run_until_complete(main())
