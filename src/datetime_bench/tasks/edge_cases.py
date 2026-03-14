# AI-ANCHOR: datetime-bench tasks: edge-case registry
"""Task Type 6: core edge cases plus randomized extras."""

from __future__ import annotations

import random
from datetime import timedelta

from ..formats import build_datetime, describe_datetime
from ..types import TaskScenario
from .base import FORMAT_KEYS, base_gold_map


TASK_TYPE = "edge_cases"


def _instruction(template: str) -> dict[str, str]:
    return {
        format_key: template.replace("{FORMAT}", format_key.replace("_", " "))
        for format_key in FORMAT_KEYS
    }


def _case(category: str, gold, template: str, tag: str) -> tuple[str, object, str, str]:
    return category, gold, template, tag


def _core_cases() -> list[tuple[str, object, str, str]]:
    return [
        _case(
            "leap_year",
            build_datetime(2024, 2, 28, 12, 0, "UTC") + timedelta(days=1),
            "What is the date and time 1 day after February 28, 2024 at noon in timezone UTC? Output in {FORMAT}.",
            "leap_positive",
        ),
        _case(
            "leap_year",
            build_datetime(2025, 2, 28, 12, 0, "UTC") + timedelta(days=1),
            "What is the date and time 1 day after February 28, 2025 at noon in timezone UTC? Output in {FORMAT}.",
            "leap_negative",
        ),
        _case(
            "month_end",
            build_datetime(2026, 1, 29, 12, 0, "UTC") + timedelta(days=3),
            "What is the date and time 3 days after January 29, 2026 at noon in timezone UTC? Output in {FORMAT}.",
            "month_rollover_a",
        ),
        _case(
            "month_end",
            build_datetime(2026, 8, 30, 18, 0, "UTC") + timedelta(days=5),
            "What is the date and time 5 days after August 30, 2026 at 6:00 PM in timezone UTC? Output in {FORMAT}.",
            "month_rollover_b",
        ),
        _case(
            "year_end",
            build_datetime(2025, 12, 31, 23, 0, "UTC") + timedelta(hours=5),
            "What is the date and time 5 hours after December 31, 2025 at 11:00 PM in timezone UTC? Output in {FORMAT}.",
            "year_rollover_a",
        ),
        _case(
            "year_end",
            build_datetime(2029, 12, 31, 22, 30, "America/Los_Angeles") + timedelta(hours=4),
            "What is the date and time 4 hours after December 31, 2029 at 10:30 PM in timezone America/Los_Angeles? Output in {FORMAT}.",
            "year_rollover_b",
        ),
        _case(
            "dst",
            build_datetime(2025, 3, 9, 1, 30, "America/New_York") + timedelta(hours=2),
            "What time is it 2 hours after March 9, 2025 at 1:30 AM in timezone America/New_York? Output in {FORMAT}.",
            "dst_us_spring",
        ),
        _case(
            "dst",
            build_datetime(2025, 11, 2, 1, 30, "America/New_York") + timedelta(hours=2),
            "What time is it 2 hours after November 2, 2025 at 1:30 AM in timezone America/New_York? Output in {FORMAT}.",
            "dst_us_fall",
        ),
        _case(
            "dst",
            build_datetime(2025, 3, 30, 1, 30, "Europe/London") + timedelta(hours=2),
            "What time is it 2 hours after March 30, 2025 at 1:30 AM in timezone Europe/London? Output in {FORMAT}.",
            "dst_london_spring",
        ),
        _case(
            "dst",
            build_datetime(2025, 10, 26, 1, 30, "Europe/London") + timedelta(hours=2),
            "What time is it 2 hours after October 26, 2025 at 1:30 AM in timezone Europe/London? Output in {FORMAT}.",
            "dst_london_fall",
        ),
        _case(
            "timezone_offset",
            build_datetime(2026, 3, 13, 12, 0, "Asia/Kolkata"),
            "Express noon on March 13, 2026 in timezone Asia/Kolkata in {FORMAT}.",
            "offset_positive",
        ),
        _case(
            "timezone_offset",
            build_datetime(2026, 3, 13, 12, 0, "America/Los_Angeles"),
            "Express noon on March 13, 2026 in timezone America/Los_Angeles in {FORMAT}.",
            "offset_negative",
        ),
        _case(
            "weekday",
            build_datetime(2026, 7, 4, 12, 0, "UTC"),
            "Express noon on July 4, 2026 in timezone UTC in {FORMAT}.",
            "weekday_july4",
        ),
        _case(
            "weekday",
            build_datetime(2028, 2, 29, 9, 0, "UTC"),
            "Express 9:00 AM on February 29, 2028 in timezone UTC in {FORMAT}.",
            "weekday_leap",
        ),
        _case(
            "century",
            build_datetime(2000, 2, 29, 10, 0, "UTC"),
            "Express February 29, 2000 at 10:00 AM in timezone UTC in {FORMAT}.",
            "century_leap",
        ),
        _case(
            "century",
            build_datetime(2100, 3, 1, 10, 0, "UTC"),
            "What is the date and time 1 day after February 28, 2100 at 10:00 AM in timezone UTC? Output in {FORMAT}.",
            "century_non_leap",
        ),
        _case(
            "midnight_noon",
            build_datetime(2026, 3, 14, 0, 0, "UTC"),
            "Express midnight at the start of March 14, 2026 in timezone UTC in {FORMAT}.",
            "midnight",
        ),
        _case(
            "midnight_noon",
            build_datetime(2026, 3, 14, 12, 0, "UTC"),
            "Express noon on March 14, 2026 in timezone UTC in {FORMAT}.",
            "noon",
        ),
        _case(
            "leap_year",
            build_datetime(2028, 2, 29, 8, 0, "Australia/Sydney"),
            "Express February 29, 2028 at 8:00 AM in timezone Australia/Sydney in {FORMAT}.",
            "leap_sydney",
        ),
        _case(
            "month_end",
            build_datetime(2026, 1, 31, 23, 30, "Asia/Tokyo") + timedelta(days=1),
            "What is the date and time 1 day after January 31, 2026 at 11:30 PM in timezone Asia/Tokyo? Output in {FORMAT}.",
            "month_rollover_c",
        ),
    ]


def _extra_leap_year(rng: random.Random, index: int) -> tuple[str, object, str, str]:
    year = rng.choice([2024, 2028, 2032])
    tz_name = rng.choice(["UTC", "Australia/Sydney", "Pacific/Auckland"])
    hour = rng.choice([8, 12, 16])
    gold = build_datetime(year, 2, 28, hour, 0, tz_name) + timedelta(days=1)
    return _case(
        "leap_year",
        gold,
        f"What is the date and time 1 day after February 28, {year} at {hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'} in timezone {tz_name}? Output in {{FORMAT}}.",
        f"leap_extra_{index:03d}",
    )


def _extra_month_end(rng: random.Random, index: int) -> tuple[str, object, str, str]:
    month = rng.choice([1, 3, 5, 7, 8, 10, 12])
    day = rng.choice([29, 30, 31])
    tz_name = rng.choice(["UTC", "Asia/Tokyo", "America/Chicago"])
    year = rng.randint(2024, 2030)
    if day > 28:
        max_day = 31 if month in {1, 3, 5, 7, 8, 10, 12} else 30
        day = min(day, max_day)
    hour = rng.choice([11, 17, 23])
    delta_days = rng.choice([1, 2, 3, 5])
    base = build_datetime(year, month, day, hour, 30 if hour == 23 else 0, tz_name)
    gold = base + timedelta(days=delta_days)
    return _case(
        "month_end",
        gold,
        f"What is the date and time {delta_days} day{'s' if delta_days != 1 else ''} after {base.strftime('%B')} {base.day}, {year} at {hour % 12 or 12}:{base.minute:02d} {'AM' if hour < 12 else 'PM'} in timezone {tz_name}? Output in {{FORMAT}}.",
        f"month_extra_{index:03d}",
    )


def _extra_year_end(rng: random.Random, index: int) -> tuple[str, object, str, str]:
    year = rng.randint(2024, 2030)
    tz_name = rng.choice(["UTC", "America/Los_Angeles", "Pacific/Auckland"])
    base = build_datetime(year, 12, 31, rng.choice([20, 22, 23]), rng.choice([0, 30]), tz_name)
    delta_hours = rng.choice([2, 4, 6])
    gold = base + timedelta(hours=delta_hours)
    return _case(
        "year_end",
        gold,
        f"What is the date and time {delta_hours} hours after December 31, {year} at {base.hour % 12 or 12}:{base.minute:02d} {'AM' if base.hour < 12 else 'PM'} in timezone {tz_name}? Output in {{FORMAT}}.",
        f"year_extra_{index:03d}",
    )


def _extra_dst(rng: random.Random, index: int) -> tuple[str, object, str, str]:
    base_options = [
        (build_datetime(2025, 3, 9, 1, 30, "America/New_York"), 2, "America/New_York"),
        (build_datetime(2025, 11, 2, 1, 30, "America/New_York"), 2, "America/New_York"),
        (build_datetime(2025, 3, 30, 1, 30, "Europe/London"), 2, "Europe/London"),
        (build_datetime(2025, 10, 26, 1, 30, "Europe/London"), 2, "Europe/London"),
        (build_datetime(2025, 4, 6, 1, 30, "Australia/Lord_Howe"), 2, "Australia/Lord_Howe"),
    ]
    base, delta_hours, tz_name = rng.choice(base_options)
    gold = base + timedelta(hours=delta_hours)
    return _case(
        "dst",
        gold,
        f"What time is it {delta_hours} hours after {base.strftime('%B')} {base.day}, {base.year} at {base.hour % 12 or 12}:{base.minute:02d} {'AM' if base.hour < 12 else 'PM'} in timezone {tz_name}? Output in {{FORMAT}}.",
        f"dst_extra_{index:03d}",
    )


def _extra_timezone_offset(rng: random.Random, index: int) -> tuple[str, object, str, str]:
    tz_name = rng.choice(["Asia/Kolkata", "America/Los_Angeles", "Australia/Lord_Howe", "Pacific/Auckland"])
    year = rng.randint(2024, 2030)
    month = rng.randint(1, 12)
    day = rng.randint(1, 28)
    gold = build_datetime(year, month, day, 12, 0, tz_name)
    return _case(
        "timezone_offset",
        gold,
        f"Express noon on {gold.strftime('%B')} {gold.day}, {gold.year} in timezone {tz_name} in {{FORMAT}}.",
        f"offset_extra_{index:03d}",
    )


def _extra_weekday(rng: random.Random, index: int) -> tuple[str, object, str, str]:
    gold = build_datetime(rng.randint(2024, 2030), rng.randint(1, 12), rng.randint(1, 28), 9, 0, "UTC")
    return _case(
        "weekday",
        gold,
        f"Express 9:00 AM on {gold.strftime('%B')} {gold.day}, {gold.year} in timezone UTC in {{FORMAT}}.",
        f"weekday_extra_{index:03d}",
    )


def _extra_century(rng: random.Random, index: int) -> tuple[str, object, str, str]:
    if rng.random() < 0.5:
        gold = build_datetime(2000, 2, 29, 10, 0, "UTC")
        prompt = "Express February 29, 2000 at 10:00 AM in timezone UTC in {FORMAT}."
    else:
        gold = build_datetime(2100, 3, 1, 10, 0, "UTC")
        prompt = "What is the date and time 1 day after February 28, 2100 at 10:00 AM in timezone UTC? Output in {FORMAT}."
    return _case("century", gold, prompt, f"century_extra_{index:03d}")


def _extra_midnight_noon(rng: random.Random, index: int) -> tuple[str, object, str, str]:
    tz_name = rng.choice(["UTC", "America/Chicago", "Pacific/Auckland"])
    base_hour = rng.choice([0, 12])
    label = "midnight" if base_hour == 0 else "noon"
    gold = build_datetime(rng.randint(2024, 2030), rng.randint(1, 12), rng.randint(1, 28), base_hour, 0, tz_name)
    prompt = (
        f"Express {label} on {gold.strftime('%B')} {gold.day}, {gold.year} in timezone {tz_name} in {{FORMAT}}."
    )
    return _case("midnight_noon", gold, prompt, f"{label}_extra_{index:03d}")


EXTRA_BUILDERS = (
    _extra_leap_year,
    _extra_month_end,
    _extra_year_end,
    _extra_dst,
    _extra_timezone_offset,
    _extra_weekday,
    _extra_century,
    _extra_midnight_noon,
)


def generate(n: int = 20, seed: int = 42) -> list[TaskScenario]:
    rng = random.Random(seed + 55)
    cases = list(_core_cases())
    while len(cases) < n:
        builder = rng.choice(EXTRA_BUILDERS)
        cases.append(builder(rng, len(cases) + 1))

    tasks: list[TaskScenario] = []
    for index, (category, gold, template, tag) in enumerate(cases[:n], start=1):
        tasks.append(
            TaskScenario(
                task_id=f"edge_{index:03d}",
                task_type=TASK_TYPE,
                gold_datetime=gold,
                instruction_by_format=_instruction(template),
                gold_formatted_by_format=base_gold_map(gold),
                metadata={"edge_category": category, "edge_tag": tag, "source_description": describe_datetime(gold)},
            )
        )
    return tasks
