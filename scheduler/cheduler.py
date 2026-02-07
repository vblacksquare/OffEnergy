
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from .mykoaliv import update_mykolaiv


scheduler = AsyncIOScheduler()
scheduler.add_job(
    id="update_mykoaliv",
    func=update_mykolaiv,
    trigger=IntervalTrigger(seconds=30),
    next_run_time=datetime.now(),
    misfire_grace_time=100
)
