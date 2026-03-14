# AI-ANCHOR: datetime-bench tasks: shared generation helpers
"""Shared helpers used by task generators."""

from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Iterable

from ..formats import format_datetime, format_task_prompt
from ..types import PromptCase, TaskScenario

FORMAT_KEYS = (
    "iso_8601",
    "rfc_3339",
    "rfc_2822",
    "natural_language",
    "javascript_date",
    "python_datetime",
    "unix_epoch",
)


def base_gold_map(dt) -> dict[str, str]:
    return {format_key: format_datetime(dt, format_key) for format_key in FORMAT_KEYS}


def case_id(task_id: str, format_key: str) -> str:
    return f"{task_id}__{format_key}"


def expand_scenarios(tasks: Iterable[TaskScenario]) -> list[PromptCase]:
    cases: list[PromptCase] = []
    for task in tasks:
        for format_key in FORMAT_KEYS:
            format_meta = dict(task.format_metadata.get(format_key, {}))
            prompt = format_task_prompt(
                task.instruction_by_format[format_key],
                format_key,
                multiple_choice=task.task_type == "multiple_choice_validation",
            )
            cases.append(
                PromptCase(
                    case_id=case_id(task.task_id, format_key),
                    task_id=task.task_id,
                    task_type=task.task_type,
                    format_key=format_key,
                    prompt=prompt,
                    gold_datetime=task.gold_datetime,
                    gold_formatted=task.gold_formatted_by_format[format_key],
                    metadata={**task.metadata, **format_meta},
                )
            )
    return cases


def shuffle_cases(cases: list[PromptCase], seed: int) -> list[PromptCase]:
    rng = random.Random(seed)
    shuffled = list(cases)
    rng.shuffle(shuffled)
    return shuffled


def write_tasks(path: Path, tasks: Iterable[TaskScenario]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = [task.to_dict() for task in tasks]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_tasks(path: Path) -> list[TaskScenario]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [TaskScenario.from_dict(item) for item in payload]
