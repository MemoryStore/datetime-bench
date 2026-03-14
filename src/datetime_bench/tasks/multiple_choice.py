# AI-ANCHOR: datetime-bench tasks: multiple-choice validation
"""Task Type 7: identify the valid representation among distractors."""

from __future__ import annotations

import random
from string import ascii_uppercase
from datetime import timedelta

from ..config import FORMAT_SPECS
from ..formats import format_datetime, random_datetime
from ..types import TaskScenario
from .base import FORMAT_KEYS, base_gold_map


TASK_TYPE = "multiple_choice_validation"


def _flip_offset_sign(value: str) -> str:
    if "+" in value[-6:]:
        return value[:-6] + value[-6:].replace("+", "-", 1)
    if "-" in value[-6:]:
        return value[:-6] + value[-6:].replace("-", "+", 1)
    if value.endswith("Z"):
        return value[:-1] + "+00:00"
    return value


def _wrong_weekday(full_name: str) -> str:
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    idx = days.index(full_name)
    return days[(idx + 1) % len(days)]


def _wrong_weekday_abbr(abbr: str) -> str:
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    idx = days.index(abbr)
    return days[(idx + 1) % len(days)]


def _iso_distractors(correct: str, gold) -> list[str]:
    alt = gold.replace(day=min(gold.day + 1, 28)).isoformat(timespec="seconds")
    return [
        correct.replace("T", " ", 1),
        _flip_offset_sign(correct),
        alt,
    ]


def _rfc3339_distractors(correct: str, gold) -> list[str]:
    alt = gold.replace(day=min(gold.day + 1, 28)).isoformat(timespec="seconds")
    return [
        correct.replace("T", " ", 1),
        _flip_offset_sign(correct),
        alt,
    ]


def _rfc_distractors(correct: str, gold) -> list[str]:
    wrong_weekday = correct.replace(correct[:3], _wrong_weekday_abbr(correct[:3]), 1)
    wrong_month = correct.replace(correct[8:11], f"{gold.month:02d}", 1)
    off_by_one = (gold.replace(day=min(gold.day + 1, 28))).strftime("%a, %d %b %Y %H:%M:%S %z")
    return [wrong_weekday, wrong_month, off_by_one]


def _nl_distractors(correct: str, gold) -> list[str]:
    wrong_day = correct.replace(gold.strftime('%A'), _wrong_weekday(gold.strftime('%A')), 1)
    wrong_ampm = correct.replace(" AM ", " PM ", 1) if " AM " in correct else correct.replace(" PM ", " AM ", 1)
    off_by_one = format_datetime(gold.replace(day=min(gold.day + 1, 28)), "natural_language")
    return [wrong_day, wrong_ampm, off_by_one]


def _javascript_distractors(correct: str, gold) -> list[str]:
    wrong_weekday = correct.replace(correct[:3], _wrong_weekday_abbr(correct[:3]), 1)
    wrong_offset = correct.replace("GMT-", "GMT+", 1) if "GMT-" in correct else correct.replace("GMT+", "GMT-", 1)
    off_by_one = format_datetime(gold.replace(day=min(gold.day + 1, 28)), "javascript_date")
    return [wrong_weekday, wrong_offset, off_by_one]


def _python_distractors(correct: str, gold) -> list[str]:
    wrong_separator = correct.replace(" ", "T", 1)
    wrong_offset = _flip_offset_sign(correct)
    off_by_one = format_datetime(gold.replace(day=min(gold.day + 1, 28)), "python_datetime")
    return [wrong_separator, wrong_offset, off_by_one]


def _unix_epoch_distractors(correct: str, gold) -> list[str]:
    epoch_seconds = int(correct)
    milliseconds = str(epoch_seconds * 1000)
    plus_hour = str(int((gold + timedelta(hours=1)).timestamp()))
    plus_day = str(int((gold + timedelta(days=1)).timestamp()))
    return [milliseconds, plus_hour, plus_day]


DISTRACTOR_BUILDERS = {
    "iso_8601": _iso_distractors,
    "rfc_3339": _rfc3339_distractors,
    "rfc_2822": _rfc_distractors,
    "natural_language": _nl_distractors,
    "javascript_date": _javascript_distractors,
    "python_datetime": _python_distractors,
    "unix_epoch": _unix_epoch_distractors,
}


def generate(n: int = 20, seed: int = 42) -> list[TaskScenario]:
    rng = random.Random(seed + 66)
    tasks: list[TaskScenario] = []
    for index in range(1, n + 1):
        gold = random_datetime(rng)
        gold_map = base_gold_map(gold)
        instruction_by_format: dict[str, str] = {}
        format_metadata: dict[str, dict[str, object]] = {}
        description = (
            f"{gold.strftime('%B')} {gold.day}, {gold.year} at "
            f"{gold.hour % 12 or 12}:{gold.minute:02d} {'AM' if gold.hour < 12 else 'PM'} "
            f"in timezone {gold.tzinfo.key if hasattr(gold.tzinfo, 'key') else gold.tzname() or 'UTC'}"
        )
        for format_key in FORMAT_KEYS:
            correct = gold_map[format_key]
            distractors = DISTRACTOR_BUILDERS[format_key](correct, gold)
            options = [correct, *distractors]
            rng.shuffle(options)
            letters = ascii_uppercase[: len(options)]
            option_lines = [f"{letter}) {value}" for letter, value in zip(letters, options, strict=True)]
            correct_letter = letters[options.index(correct)]
            instruction_by_format[format_key] = (
                f"Which of the following is a valid {FORMAT_SPECS[format_key]['name']} representation of {description}?\n\n"
                + "\n".join(option_lines)
            )
            format_metadata[format_key] = {
                "correct_choice": correct_letter,
                "options": {letter: value for letter, value in zip(letters, options, strict=True)},
                "description": description,
            }
        tasks.append(
            TaskScenario(
                task_id=f"mc_{index:03d}",
                task_type=TASK_TYPE,
                gold_datetime=gold,
                instruction_by_format=instruction_by_format,
                gold_formatted_by_format=gold_map,
                format_metadata=format_metadata,
            )
        )
    return tasks
