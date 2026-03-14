# AI-ANCHOR: datetime-bench: shared task & result types
"""Dataclasses used by task generation, execution, and analysis."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class TaskScenario:
    task_id: str
    task_type: str
    gold_datetime: datetime
    instruction_by_format: dict[str, str]
    gold_formatted_by_format: dict[str, str]
    metadata: dict[str, Any] = field(default_factory=dict)
    format_metadata: dict[str, dict[str, Any]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        payload = asdict(self)
        payload["gold_datetime"] = self.gold_datetime.isoformat()
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> "TaskScenario":
        data = dict(payload)
        data["gold_datetime"] = datetime.fromisoformat(payload["gold_datetime"])
        return cls(**data)


@dataclass(slots=True)
class PromptCase:
    case_id: str
    task_id: str
    task_type: str
    format_key: str
    prompt: str
    gold_datetime: datetime
    gold_formatted: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class SelectedModel:
    cell: str
    label: str
    requested_candidates: list[str]
    selected_model: str | None
    reasoning_mode: str
    size: str
    reasoning_config: dict[str, Any] | None
    pricing: dict[str, float]
    notes: list[str] = field(default_factory=list)

    def estimated_unit_cost(self) -> float:
        prompt_cost = float(self.pricing.get("prompt", 0.0))
        completion_cost = float(self.pricing.get("completion", 0.0))
        reasoning_cost = float(self.pricing.get("internal_reasoning", completion_cost))
        return prompt_cost + completion_cost + reasoning_cost


@dataclass(slots=True)
class ParseResult:
    cleaned_output: str
    syntactic_valid: bool
    parsed_datetime: datetime | None = None
    parse_mode: str | None = None
    warnings: list[str] = field(default_factory=list)
    selected_choice: str | None = None
    selected_option_content: str | None = None


@dataclass(slots=True)
class EvaluationResult:
    syntactic_valid: bool
    semantic_correct: bool
    strict_correct: bool
    calendar_consistent: bool | None
    format_compliance: float
    extraction_clean: bool
    error_type: str | None
    error_subtype: str | None
    delta_seconds: float | None
    parse_mode: str | None
    warnings: list[str] = field(default_factory=list)
    selected_choice: str | None = None
    selected_option_content: str | None = None
