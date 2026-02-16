
from aiogram import Router

from .start import start_router
from .language import language_router
from .utils import utils_router
from .city import city_router
from .queue import queue_router
from .nots import nots_router
from .schedule import schedule_router
from .circle import circle_router


root_router = Router()
root_router.include_routers(
    start_router,
    language_router,
    city_router,
    queue_router,
    nots_router,
    schedule_router,
    circle_router,
    utils_router
)
