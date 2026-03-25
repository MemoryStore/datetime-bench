# AI-ANCHOR: datetime-bench tasks: registry and persistence
"""Task registry for the datetime benchmark."""

from __future__ import annotations

from pathlib import Path

from ..config import SEED, TASKS_DIR, TASKS_FILENAME, TASKS_PER_TYPE, TASKS_PER_TYPE_MAP
from ..types import PromptCase, TaskScenario
from . import (
    direct_generation,
    edge_cases,
    extraction,
    format_conversion,
    multi_hop,
    parsing_normalization,
    temporal_arithmetic,
)
from .base import expand_scenarios, read_tasks, shuffle_cases, write_tasks

TASK_GENERATORS = (
    (direct_generation.TASK_TYPE, direct_generation.generate),
    (temporal_arithmetic.TASK_TYPE, temporal_arithmetic.generate),
    (multi_hop.TASK_TYPE, multi_hop.generate),
    (format_conversion.TASK_TYPE, format_conversion.generate),
    (extraction.TASK_TYPE, extraction.generate),
    (edge_cases.TASK_TYPE, edge_cases.generate),
    (parsing_normalization.TASK_TYPE, parsing_normalization.generate),
)


def generate_all_tasks(
    n: int | None = None,
    seed: int = SEED,
    task_counts: dict[str, int] | None = None,
) -> list[TaskScenario]:
    counts = task_counts or TASKS_PER_TYPE_MAP
    tasks: list[TaskScenario] = []
    for task_type, generator in TASK_GENERATORS:
        task_n = n if n is not None else counts.get(task_type, TASKS_PER_TYPE)
        tasks.extend(generator(n=task_n, seed=seed))
    return tasks


def default_tasks_path(seed: int = SEED, *, tasks_dir: Path = TASKS_DIR) -> Path:
    return tasks_dir / TASKS_FILENAME.replace(str(SEED), str(seed))


def save_generated_tasks(
    tasks: list[TaskScenario],
    path: Path | None = None,
    *,
    tasks_dir: Path = TASKS_DIR,
) -> Path:
    out_path = path or default_tasks_path(tasks_dir=tasks_dir)
    write_tasks(out_path, tasks)
    return out_path


def load_generated_tasks(path: Path) -> list[TaskScenario]:
    return read_tasks(path)


def build_cases(tasks: list[TaskScenario], seed: int = SEED) -> list[PromptCase]:
    return shuffle_cases(expand_scenarios(tasks), seed=seed)
