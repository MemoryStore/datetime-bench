# AI-ANCHOR: datetime-bench: datetime formatting helpers
"""Formatting and date utility helpers for the benchmark."""

from __future__ import annotations

import calendar
from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

from .config import FORMAT_SPECS, TIMEZONES

WEEKDAY_ABBR = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_FULL = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]
MONTH_ABBR = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]

JAVASCRIPT_TZ_NAMES = {
    "UTC": {"UTC": "Coordinated Universal Time"},
    "America/New_York": {
        "EST": "Eastern Standard Time",
        "EDT": "Eastern Daylight Time",
    },
    "America/Los_Angeles": {
        "PST": "Pacific Standard Time",
        "PDT": "Pacific Daylight Time",
    },
    "America/Chicago": {
        "CST": "Central Standard Time",
        "CDT": "Central Daylight Time",
    },
    "Europe/London": {
        "GMT": "Greenwich Mean Time",
        "BST": "British Summer Time",
    },
    "Europe/Berlin": {
        "CET": "Central European Standard Time",
        "CEST": "Central European Summer Time",
    },
    "Asia/Tokyo": {
        "JST": "Japan Standard Time",
    },
    "Australia/Sydney": {
        "AEST": "Australian Eastern Standard Time",
        "AEDT": "Australian Eastern Daylight Time",
    },
    "Australia/Lord_Howe": {
        "LHST": "Lord Howe Standard Time",
        "LHDT": "Lord Howe Daylight Time",
    },
    "Pacific/Auckland": {
        "NZST": "New Zealand Standard Time",
        "NZDT": "New Zealand Daylight Time",
    },
    "Asia/Kolkata": {
        "IST": "India Standard Time",
    },
}


def zone(name: str) -> ZoneInfo:
    return ZoneInfo(name)


def random_datetime_components(rng) -> tuple[int, int, int, int, int, str]:
    tz_name = rng.choice(TIMEZONES)
    year = rng.randint(2020, 2030)
    month = rng.randint(1, 12)
    max_day = calendar.monthrange(year, month)[1]
    day = rng.randint(1, max_day)
    hour = rng.randint(6, 20)
    minute = rng.choice([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55])
    return year, month, day, hour, minute, tz_name


def build_datetime(
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    tz_name: str,
    second: int = 0,
) -> datetime:
    return datetime(year, month, day, hour, minute, second, tzinfo=zone(tz_name))


def random_datetime(rng) -> datetime:
    return build_datetime(*random_datetime_components(rng))


def to_iso_8601(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def to_rfc_3339(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def to_rfc_2822(dt: datetime) -> str:
    return dt.strftime("%a, %d %b %Y %H:%M:%S %z")


def to_natural_language(dt: datetime) -> str:
    hour = dt.hour % 12 or 12
    minute = f"{dt.minute:02d}"
    ampm = "AM" if dt.hour < 12 else "PM"
    zone_name = dt.tzname() or dt.strftime("%z")
    return f"{dt.strftime('%A')}, {dt.strftime('%B')} {dt.day}, {dt.year} at {hour}:{minute} {ampm} {zone_name}"


def to_javascript_date(dt: datetime) -> str:
    tz_key = dt.tzinfo.key if hasattr(dt.tzinfo, "key") else None
    zone_token = dt.tzname() or dt.strftime("%z")
    zone_name = JAVASCRIPT_TZ_NAMES.get(tz_key or "", {}).get(zone_token, zone_token)
    return f"{dt.strftime('%a %b %d %Y %H:%M:%S')} GMT{dt.strftime('%z')} ({zone_name})"


def to_python_datetime(dt: datetime) -> str:
    return dt.isoformat(sep=" ", timespec="seconds")


def to_unix_epoch(dt: datetime) -> str:
    return str(int(dt.astimezone(UTC).timestamp()))


def format_datetime(dt: datetime, format_key: str) -> str:
    if format_key == "iso_8601":
        return to_iso_8601(dt)
    if format_key == "rfc_3339":
        return to_rfc_3339(dt)
    if format_key == "rfc_2822":
        return to_rfc_2822(dt)
    if format_key == "natural_language":
        return to_natural_language(dt)
    if format_key == "javascript_date":
        return to_javascript_date(dt)
    if format_key == "python_datetime":
        return to_python_datetime(dt)
    if format_key == "unix_epoch":
        return to_unix_epoch(dt)
    raise KeyError(format_key)


def format_task_prompt(instruction: str, format_key: str, multiple_choice: bool = False) -> str:
    spec = FORMAT_SPECS[format_key]
    parts = [
        instruction,
        "",
        f"Output format: {spec['name']}",
        f"Expected format pattern: {spec['pattern']}",
        f"Example of this format: {spec['example']}",
    ]
    if multiple_choice:
        parts.append("Respond with ONLY the letter (A, B, C, or D).")
    parts.extend(["", "Your answer:"])
    return "\n".join(parts)


def describe_datetime(dt: datetime) -> str:
    local_hour = dt.hour % 12 or 12
    ampm = "AM" if dt.hour < 12 else "PM"
    return (
        f"{dt.strftime('%B')} {dt.day}, {dt.year} at {local_hour}:{dt.minute:02d} {ampm} "
        f"in timezone {dt.tzinfo.key if hasattr(dt.tzinfo, 'key') else dt.tzname() or 'UTC'}"
    )


def nth_weekday_of_month(year: int, month: int, weekday: int, occurrence: int) -> date:
    current = date(year, month, 1)
    seen = 0
    while current.month == month:
        if current.weekday() == weekday:
            seen += 1
            if seen == occurrence:
                return current
        current += timedelta(days=1)
    msg = f"No {occurrence} weekday {weekday} in {year}-{month}"
    raise ValueError(msg)


def next_weekday(dt: datetime, weekday: int) -> datetime:
    days_ahead = (weekday - dt.weekday()) % 7
    days_ahead = 7 if days_ahead == 0 else days_ahead
    return dt + timedelta(days=days_ahead)


def same_local_time(dt: datetime, tz_name: str) -> datetime:
    tz = zone(tz_name)
    return dt.astimezone(tz)


def utc(dt: datetime) -> datetime:
    return dt.astimezone(UTC)
