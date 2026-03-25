# AI-ANCHOR: datetime-bench tasks: temporal arithmetic cases
"""Task Type 2: arithmetic over explicit datetimes."""

from __future__ import annotations

import random
from datetime import timedelta

from ..formats import build_datetime, random_datetime
from ..types import TaskScenario
from .base import FORMAT_KEYS, base_gold_map
from .variants import describe_datetime_variant, normalize_timezone_for_representation, variant_for_index


TASK_TYPE = "temporal_arithmetic"

DST_CASES = [
    (
        build_datetime(2025, 3, 9, 1, 0, "America/New_York"),
        3,
        "hours",
        "dst_spring_forward_us_east",
    ),
    (
        build_datetime(2025, 11, 2, 0, 30, "America/New_York"),
        3,
        "hours",
        "dst_fall_back_us_east",
    ),
    (
        build_datetime(2025, 3, 30, 0, 30, "Europe/London"),
        3,
        "hours",
        "dst_spring_forward_london",
    ),
    (
        build_datetime(2025, 10, 26, 0, 30, "Europe/London"),
        3,
        "hours",
        "dst_fall_back_london",
    ),
]


def _apply_delta(base, amount: int, unit: str):
    if unit == "hours":
        return base + timedelta(hours=amount)
    if unit == "days":
        return base + timedelta(days=amount)
    if unit == "weeks":
        return base + timedelta(weeks=amount)
    raise KeyError(unit)


def generate(n: int = 20, seed: int = 42) -> list[TaskScenario]:
    rng = random.Random(seed + 22)
    tasks: list[TaskScenario] = []
    presets = list(DST_CASES)
    for index in range(1, n + 1):
        input_style, timezone_representation = variant_for_index(index)
        if input_style in {"prose_messy", "ambiguous_but_resolved"}:
            input_style = "compact_structured" if index % 2 == 0 else "canonical_text"
        if presets:
            base, amount, unit, tag = presets.pop(0)
            input_style = "canonical_text"
            timezone_representation = "iana_zone"
        else:
            base = normalize_timezone_for_representation(random_datetime(rng), timezone_representation)
            unit = rng.choice(["hours", "days", "weeks"])
            amount = rng.randint(1, 90)
            tag = "random"
        gold = _apply_delta(base, amount, unit)
        base_description = describe_datetime_variant(
            base,
            input_style,
            timezone_representation,
            assume_mdy=index % 2 == 1,
        )
        instruction = (
            f"What is the date and time exactly {amount} {unit} after "
            f"{base_description}? Output in {{FORMAT}}."
        )
        instruction_by_format = {
            format_key: instruction.replace("{FORMAT}", format_key.replace("_", " "))
            for format_key in FORMAT_KEYS
        }
        tasks.append(
            TaskScenario(
                task_id=f"temporal_arith_{index:03d}",
                task_type=TASK_TYPE,
                gold_datetime=gold,
                instruction_by_format=instruction_by_format,
                gold_formatted_by_format=base_gold_map(gold),
                metadata={
                    "base_datetime": base.isoformat(),
                    "amount": amount,
                    "unit": unit,
                    "case_tag": tag,
                    "input_style": input_style,
                    "timezone_representation": timezone_representation,
                },
            )
        )
    return tasks
