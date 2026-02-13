
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from .mykoaliv import update_mykolaiv
from .change import update_pusher
from .state import update_state


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
    trigger=CronTrigger(minute='15,20', second=10),
    next_run_time=datetime.now(),
    misfire_grace_time=100
)
