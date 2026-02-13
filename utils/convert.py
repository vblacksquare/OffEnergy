
from typing import Optional
from datetime import datetime
from uuid import uuid3, NAMESPACE_URL

from models import Schedule


def string_to_uuid(string: str) -> str:
    return uuid3(NAMESPACE_URL, string.lower()).hex


def from_hours(date: str | datetime) -> float:
    if isinstance(date, str):
        hours, minutes, seconds = map(int, date.split(":"))

    else:
        hours, minutes, seconds = date.hour, date.minute, date.second

    return hours + (minutes / 60)


def to_hours(value: float) -> str:
    parts = str(value).split(".")
    parts[1] = str(round((int(parts[1]) / 10) * 60))

    for i, part in enumerate(parts):
        if len(part) != 2:
            parts[i] = f"0{part}"

    return ':'.join(parts)


def join_schedule(docs: list[Schedule], now: datetime, language: str) -> str:
    from bot import i18n

    joined = get_joined_schedule(docs)

    parts = []
    hours_now = from_hours(now)

    for doc in joined:
        if doc.start_at <= hours_now < (doc.end_at if doc.end_at > doc.start_at else 24 + doc.end_at):
            row = "current_row"

        else:
            row = "row"

        parts.append(
            i18n.gettext(row, locale=language).format(
                start_at=to_hours(doc.start_at),
                end_at=to_hours(doc.end_at),
                status=i18n.gettext(doc.status.value, locale=language),
            )
        )

    schedule = '\n'.join(parts)

    return schedule


def get_joined_schedule(docs: list[Schedule]) -> list[Schedule]:
    by_time_seria: dict[str, Optional[Schedule]] = {}

    for doc in docs:
        if doc.time_seria not in by_time_seria:
            by_time_seria[doc.time_seria] = None

        old_doc = by_time_seria[doc.time_seria]
        if old_doc is None:
            by_time_seria[doc.time_seria] = doc

        elif old_doc.created_at < doc.created_at:
            by_time_seria[doc.time_seria] = doc

    docs = sorted(
        list(by_time_seria.values()),
        key=lambda x: x.start_at
    )

    joined = []
    current_doc = docs[0]

    for doc in docs[1:]:
        if doc.status == current_doc.status:
            current_doc.end_at = doc.end_at

        else:
            joined.append(current_doc)
            current_doc = doc

    joined.append(current_doc)

    return joined


def to_time_left(hours: float, language: str, only_minutes: bool) -> str:
    from bot import i18n

    hours, minutes = str(hours).split(".")

    hours = int(hours)

    if len(minutes) == 1:
        minutes = minutes + "0"
    minutes = round(int(minutes) * 0.6)

    parts = []
    if hours and hours > 0:
        parts.append(
            i18n.gettext(
                "hours",
                "hours_remind",
                hours,
                locale=language
            ) % hours
        )

    if minutes and minutes > 0:
        parts.append(
            i18n.gettext(
                "minutes",
                "minutes_remind",
                minutes,
                locale=language
            ) % minutes
        )

    if not len(parts):
        return i18n.gettext("now", locale=language)

    return ", ".join(parts)
