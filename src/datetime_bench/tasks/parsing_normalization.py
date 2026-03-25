# AI-ANCHOR: datetime-bench tasks: parsing and normalization
"""Task Type 7: parse varied datetime inputs and normalize them."""

from __future__ import annotations

import random

from ..formats import random_datetime
from ..types import TaskScenario
from .base import FORMAT_KEYS, base_gold_map
from .variants import describe_datetime_variant, normalize_timezone_for_representation, variant_for_index


TASK_TYPE = "parsing_normalization"


def generate(n: int = 20, seed: int = 42) -> list[TaskScenario]:
    rng = random.Random(seed + 77)
    tasks: list[TaskScenario] = []
    for index in range(1, n + 1):
        input_style, timezone_representation = variant_for_index(index)
        gold = normalize_timezone_for_representation(random_datetime(rng), timezone_representation)
        assume_mdy = index % 2 == 1
        source_value = describe_datetime_variant(
            gold,
            input_style,
            timezone_representation,
            assume_mdy=assume_mdy,
        )
        instruction_by_format = {
            format_key: (
                "Parse and normalize the following datetime expression. "
                f"Output in {format_key.replace('_', ' ')}: {source_value}"
            )
            for format_key in FORMAT_KEYS
        }
        tasks.append(
            TaskScenario(
                task_id=f"parse_norm_{index:03d}",
                task_type=TASK_TYPE,
                gold_datetime=gold,
                instruction_by_format=instruction_by_format,
                gold_formatted_by_format=base_gold_map(gold),
                metadata={
                    "input_style": input_style,
                    "timezone_representation": timezone_representation,
                    "source_representation": source_value,
                    "assume_mdy": assume_mdy,
                },
            )
        )
    return tasks
