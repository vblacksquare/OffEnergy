
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from .mykoaliv import update_mykolaiv
from .change import update_pusher
from .state import update_state
from .teror import update_teror


scheduler = AsyncIOScheduler()
scheduler.add_job(
    id="update_mykoaliv",
    func=update_mykolaiv,
    trigger=IntervalTrigger(seconds=30),
    next_run_time=datetime.now(),
    misfire_grace_time=100
)
scheduler.add_job(
    id="update_pusher",
    func=update_pusher,
    trigger=IntervalTrigger(seconds=30),
    next_run_time=datetime.now(),
    misfire_grace_time=100
)
scheduler.add_job(
    id="update_state",
    func=update_state,
    trigger=CronTrigger(minute='0,30', second=10),
    misfire_grace_time=100
)
scheduler.add_job(
    id="update_teror",
    func=update_teror,
    trigger=CronTrigger(hour="14,02"),
    misfire_grace_time=100
)
