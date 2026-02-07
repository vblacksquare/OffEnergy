
from datetime import datetime
from uuid import uuid3, NAMESPACE_URL


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
