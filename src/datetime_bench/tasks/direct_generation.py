# AI-ANCHOR: datetime-bench tasks: direct format generation
"""Task Type 1: direct datetime generation."""

from __future__ import annotations

import random

from ..formats import describe_datetime, random_datetime
from ..types import TaskScenario
from .base import FORMAT_KEYS, base_gold_map


TASK_TYPE = "direct_generation"


def generate(n: int = 20, seed: int = 42) -> list[TaskScenario]:
    rng = random.Random(seed + 11)
    tasks: list[TaskScenario] = []
    for index in range(1, n + 1):
        gold = random_datetime(rng)
        instruction_by_format = {
            format_key: (
                f"Convert the following datetime to {format_key.replace('_', ' ')}: "
                f"{describe_datetime(gold)}"
            )
            for format_key in FORMAT_KEYS
        }
        tasks.append(
            TaskScenario(
                task_id=f"direct_gen_{index:03d}",
                task_type=TASK_TYPE,
                gold_datetime=gold,
                instruction_by_format=instruction_by_format,
                gold_formatted_by_format=base_gold_map(gold),
                metadata={"source_description": describe_datetime(gold)},
            )
        )
    return tasks
