# AI-ANCHOR: datetime-bench: experiment config & paths
"""Shared configuration for the datetime benchmark."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from . import layout as _layout
from .layout import make_layout

SEED = 42
TASKS_PER_TYPE = 20
TASKS_PER_TYPE_MAP: dict[str, int] = {
    "direct_generation": 35,
    "temporal_arithmetic": 40,
    "multi_hop_reasoning": 35,
    "format_conversion": 35,
    "extraction_from_passage": 30,
    "edge_cases": 35,
    "multiple_choice_validation": 25,
}
SEMANTIC_THRESHOLDS_SECONDS: dict[str, float] = {
    "default": 0.0,
    "multi_hop_reasoning": 60.0,
    "extraction_from_passage": 60.0,
}
MAX_COMPLETION_TOKENS = 300
TEMPERATURE = 0.0
API_TIMEOUT_SECONDS = 60.0
REQUEST_RETRIES = 3
REQUEST_DELAY_SECONDS = 0.3
MAX_CONCURRENCY = 24
CELL_PARALLELISM = 12
SOFT_BUDGET_CAP_USD = 250.0
HARD_BUDGET_CAP_USD = 300.0
TASKS_FILENAME = f"tasks_seed{SEED}.json"
BENCH_VERSION = "v0.2"
PREVIOUS_BENCH_VERSION = "v0.1.5"

SYSTEM_PROMPT = (
    "You are a datetime formatting assistant. You will be given a task involving\n"
    "dates and times. Respond with ONLY the requested output - no explanation,\n"
    "no prose, no markdown formatting, no quotes. Just the datetime string (or\n"
    "the letter for multiple choice questions)."
)

DEFAULT_LAYOUT = make_layout(
    run_slug=f"datetime_bench_{BENCH_VERSION}",
    report_slug=f"datetime_bench_{BENCH_VERSION}",
    version=BENCH_VERSION,
    previous_version=PREVIOUS_BENCH_VERSION,
)
REPO_ROOT = _layout.REPO_ROOT
BENCH_ROOT = _layout.BENCH_ROOT
RUN_ROOT = DEFAULT_LAYOUT.run_root
RESULTS_DIR = DEFAULT_LAYOUT.results_dir
TASKS_DIR = DEFAULT_LAYOUT.tasks_dir
REPORTS_DIR = DEFAULT_LAYOUT.report_dir
LOG_FILE = DEFAULT_LAYOUT.log_file
MODEL_SELECTION_FILE = DEFAULT_LAYOUT.model_selection_file
DRY_RUN_FILE = DEFAULT_LAYOUT.dry_run_file
RUN_SUMMARY_FILE = DEFAULT_LAYOUT.run_summary_file
RUN_MANIFEST_FILE = DEFAULT_LAYOUT.run_manifest_file
RAW_RESULTS_CSV = DEFAULT_LAYOUT.raw_results_csv
SUMMARY_MD = DEFAULT_LAYOUT.summary_md
FORMAT_COMPARISON_CSV = DEFAULT_LAYOUT.format_comparison_csv
ERROR_TAXONOMY_CSV = DEFAULT_LAYOUT.error_taxonomy_csv
COST_REPORT_CSV = DEFAULT_LAYOUT.cost_report_csv
PRIMARY_RESULTS_CSV = DEFAULT_LAYOUT.primary_results_csv
CHARTS_DIR = DEFAULT_LAYOUT.charts_dir

FORMAT_SPECS: dict[str, dict[str, str]] = {
    "iso_8601": {
        "name": "ISO 8601",
        "pattern": "YYYY-MM-DDTHH:MM:SS±HH:MM",
        "example": "2025-01-15T09:30:00-05:00",
    },
    "rfc_3339": {
        "name": "RFC 3339",
        "pattern": "YYYY-MM-DDTHH:MM:SS±HH:MM",
        "example": "2025-01-15T09:30:00-05:00",
    },
    "rfc_2822": {
        "name": "RFC 2822",
        "pattern": "Day, DD Mon YYYY HH:MM:SS ±HHMM",
        "example": "Wed, 15 Jan 2025 09:30:00 -0500",
    },
    "natural_language": {
        "name": "Structured Natural Language",
        "pattern": "Weekday, Month DD, YYYY at H:MM AM/PM Timezone",
        "example": "Wednesday, January 15, 2025 at 9:30 AM EST",
    },
    "javascript_date": {
        "name": "JavaScript Date.toString()",
        "pattern": "Day Mon DD YYYY HH:MM:SS GMT±HHMM (Time Zone Name)",
        "example": "Wed Jan 15 2025 09:30:00 GMT-0500 (Eastern Standard Time)",
    },
    "python_datetime": {
        "name": "Python str(datetime)",
        "pattern": "YYYY-MM-DD HH:MM:SS±HH:MM",
        "example": "2025-01-15 09:30:00-05:00",
    },
    "unix_epoch": {
        "name": "Unix Epoch Seconds",
        "pattern": "1736951400",
        "example": "1736951400",
    },
}

TIMEZONES = [
    "UTC",
    "America/New_York",
    "America/Los_Angeles",
    "America/Chicago",
    "Europe/London",
    "Europe/Berlin",
    "Asia/Tokyo",
    "Australia/Sydney",
    "Australia/Lord_Howe",
    "Pacific/Auckland",
    "Asia/Kolkata",
]


@dataclass(frozen=True)
class ModelCell:
    cell: str
    label: str
    reasoning_mode: str
    size: str
    candidates: tuple[str, ...]
    reasoning_config: dict[str, Any] | None = None


# AI-ANCHOR: datetime-bench v0.2: 24-cell model matrix
# 3 frontier families × 3 sizes × 2 reasoning modes + 6 open-source cells.
# Enables within-family size comparison, cross-family comparison at each size,
# and reasoning effect isolation. Cells where the primary model fails probe
# are skipped (not substituted from another family).
MODEL_CELLS: tuple[ModelCell, ...] = (
    # --- Google: small / medium / large × non-reasoning / reasoning ---
    ModelCell(
        cell="google_small_nr",
        label="Google small, non-reasoning",
        reasoning_mode="non_reasoning",
        size="small",
        candidates=(
            "google/gemini-3.1-flash-lite",
            "google/gemini-3.1-flash-lite-preview",
        ),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="google_small_r",
        label="Google small, reasoning",
        reasoning_mode="reasoning",
        size="small",
        candidates=(
            "google/gemini-3-flash",
            "google/gemini-3-flash-preview",
        ),
        reasoning_config={"effort": "minimal", "exclude": True},
    ),
    ModelCell(
        cell="google_med_nr",
        label="Google medium, non-reasoning",
        reasoning_mode="non_reasoning",
        size="medium",
        candidates=(
            "google/gemini-3.1-flash",
            "google/gemini-3.1-flash-preview",
        ),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="google_med_r",
        label="Google medium, reasoning",
        reasoning_mode="reasoning",
        size="medium",
        candidates=(
            "google/gemini-3.1-flash",
            "google/gemini-3.1-flash-preview",
        ),
        reasoning_config={"effort": "medium", "exclude": True},
    ),
    ModelCell(
        cell="google_large_nr",
        label="Google large, non-reasoning",
        reasoning_mode="non_reasoning",
        size="large",
        candidates=(
            "google/gemini-3.1-pro",
            "google/gemini-3.1-pro-preview",
        ),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="google_large_r",
        label="Google large, reasoning",
        reasoning_mode="reasoning",
        size="large",
        candidates=(
            "google/gemini-3.1-pro",
            "google/gemini-3.1-pro-preview",
        ),
        reasoning_config={"effort": "high", "exclude": True},
    ),
    # --- Anthropic: small / medium / large × non-reasoning / reasoning ---
    ModelCell(
        cell="anthropic_small_nr",
        label="Anthropic small, non-reasoning",
        reasoning_mode="non_reasoning",
        size="small",
        candidates=("anthropic/claude-haiku-4.5",),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="anthropic_small_r",
        label="Anthropic small, reasoning",
        reasoning_mode="reasoning",
        size="small",
        candidates=("anthropic/claude-haiku-4.5",),
        reasoning_config={"max_tokens": 1024, "exclude": True},
    ),
    ModelCell(
        cell="anthropic_med_nr",
        label="Anthropic medium, non-reasoning",
        reasoning_mode="non_reasoning",
        size="medium",
        candidates=("anthropic/claude-sonnet-4.6",),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="anthropic_med_r",
        label="Anthropic medium, reasoning",
        reasoning_mode="reasoning",
        size="medium",
        candidates=("anthropic/claude-sonnet-4.6",),
        reasoning_config={"max_tokens": 2048, "exclude": True},
    ),
    ModelCell(
        cell="anthropic_large_nr",
        label="Anthropic large, non-reasoning",
        reasoning_mode="non_reasoning",
        size="large",
        candidates=("anthropic/claude-opus-4.6",),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="anthropic_large_r",
        label="Anthropic large, reasoning",
        reasoning_mode="reasoning",
        size="large",
        candidates=("anthropic/claude-opus-4.6",),
        reasoning_config={"max_tokens": 2048, "exclude": True},
    ),
    # --- OpenAI: small / medium / large × non-reasoning / reasoning ---
    ModelCell(
        cell="openai_small_nr",
        label="OpenAI small, non-reasoning",
        reasoning_mode="non_reasoning",
        size="small",
        candidates=(
            "openai/gpt-5-mini",
            "openai/gpt-5.3-instant",
            "openai/gpt-5.3-chat",
        ),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="openai_small_r",
        label="OpenAI small, reasoning",
        reasoning_mode="reasoning",
        size="small",
        candidates=(
            "openai/gpt-5-mini",
            "openai/gpt-5.3-instant",
        ),
        reasoning_config={"effort": "low", "exclude": True},
    ),
    ModelCell(
        cell="openai_med_nr",
        label="OpenAI medium, non-reasoning",
        reasoning_mode="non_reasoning",
        size="medium",
        candidates=(
            "openai/gpt-5.1",
            "openai/gpt-5.4",
        ),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="openai_med_r",
        label="OpenAI medium, reasoning",
        reasoning_mode="reasoning",
        size="medium",
        candidates=(
            "openai/gpt-5.1",
            "openai/gpt-5.4",
        ),
        reasoning_config={"effort": "medium", "exclude": True},
    ),
    ModelCell(
        cell="openai_large_nr",
        label="OpenAI large, non-reasoning",
        reasoning_mode="non_reasoning",
        size="large",
        candidates=("openai/gpt-5.4",),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="openai_large_r",
        label="OpenAI large, reasoning",
        reasoning_mode="reasoning",
        size="large",
        candidates=("openai/gpt-5.4",),
        reasoning_config={"effort": "high", "exclude": True},
    ),
    # --- Open-Source contenders ---
    ModelCell(
        cell="qwen_small_nr",
        label="Qwen 3.5 9B, non-reasoning",
        reasoning_mode="non_reasoning",
        size="small",
        candidates=(
            "qwen/qwen3.5-9b",
            "qwen/qwen-3.5-9b",
        ),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="qwen_small_r",
        label="Qwen 3.5 9B, reasoning",
        reasoning_mode="reasoning",
        size="small",
        candidates=(
            "qwen/qwen3.5-9b",
            "qwen/qwen-3.5-9b",
        ),
        reasoning_config={"effort": "low", "exclude": True},
    ),
    ModelCell(
        cell="qwen_large_nr",
        label="Qwen 3.5 27B, non-reasoning",
        reasoning_mode="non_reasoning",
        size="large",
        candidates=(
            "qwen/qwen3.5-27b",
            "qwen/qwen-3.5-27b",
        ),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="qwen_large_r",
        label="Qwen 3.5 27B, reasoning",
        reasoning_mode="reasoning",
        size="large",
        candidates=(
            "qwen/qwen3.5-27b",
            "qwen/qwen-3.5-27b",
        ),
        reasoning_config={"effort": "medium", "exclude": True},
    ),
    ModelCell(
        cell="glm_med_nr",
        label="GLM-5, non-reasoning",
        reasoning_mode="non_reasoning",
        size="medium",
        candidates=(
            "zhipu/glm-5",
            "thudm/glm-5",
        ),
        reasoning_config={"enabled": False},
    ),
    ModelCell(
        cell="glm_med_r",
        label="GLM-5, reasoning",
        reasoning_mode="reasoning",
        size="medium",
        candidates=(
            "zhipu/glm-5",
            "thudm/glm-5",
        ),
        reasoning_config={"effort": "medium", "exclude": True},
    ),
)
