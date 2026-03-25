# AI-ANCHOR: datetime-bench tasks: format conversion prompts
"""Task Type 4: convert one datetime format into another."""

from __future__ import annotations

import random

from ..formats import format_datetime, random_datetime
from ..types import TaskScenario
from .base import FORMAT_KEYS, base_gold_map


TASK_TYPE = "format_conversion"


def generate(n: int = 20, seed: int = 42) -> list[TaskScenario]:
    rng = random.Random(seed + 44)
    tasks: list[TaskScenario] = []
    for index in range(1, n + 1):
        gold = random_datetime(rng)
        instruction_by_format: dict[str, str] = {}
        format_metadata: dict[str, dict[str, str]] = {}
        for format_key in FORMAT_KEYS:
            other_formats = [item for item in FORMAT_KEYS if item != format_key]
            source_format = rng.choice(other_formats)
            source_value = format_datetime(gold, source_format)
            instruction_by_format[format_key] = (
                f"Convert the following {source_format.replace('_', ' ')} datetime to "
                f"{format_key.replace('_', ' ')}: {source_value}"
            )
            format_metadata[format_key] = {
                "source_format": source_format,
                "source_value": source_value,
            }
        tasks.append(
            TaskScenario(
                task_id=f"format_conv_{index:03d}",
                task_type=TASK_TYPE,
                gold_datetime=gold,
                instruction_by_format=instruction_by_format,
                gold_formatted_by_format=base_gold_map(gold),
                format_metadata=format_metadata,
                metadata={
                    "input_style": "compact_structured",
                },
            )
        )
    return tasks
