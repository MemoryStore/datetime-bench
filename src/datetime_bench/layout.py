# AI-ANCHOR: datetime-bench: versioned artifact layout
"""Versioned run/report path helpers and manifest metadata."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
BENCH_ROOT = REPO_ROOT


@dataclass(frozen=True, slots=True)
class RunLayout:
    """Resolved artifact paths for a single benchmark run namespace."""

    benchmark_name: str
    run_root: Path
    report_dir: Path
    version: str | None = None
    previous_version: str | None = None
    run_slug: str | None = None
    report_slug: str | None = None

    @property
    def results_dir(self) -> Path:
        return self.run_root / "results"

    @property
    def tasks_dir(self) -> Path:
        return self.run_root / "tasks"

    @property
    def log_file(self) -> Path:
        return self.run_root / "datetime-bench.log"

    @property
    def model_selection_file(self) -> Path:
        return self.run_root / "model_selection.json"

    @property
    def dry_run_file(self) -> Path:
        return self.run_root / "dry_run.json"

    @property
    def run_summary_file(self) -> Path:
        return self.run_root / "run_summary.json"

    @property
    def run_manifest_file(self) -> Path:
        return self.run_root / "run_manifest.json"

    @property
    def raw_results_csv(self) -> Path:
        return self.report_dir / "results_all.csv"

    @property
    def summary_md(self) -> Path:
        return self.report_dir / "summary.md"

    @property
    def format_comparison_csv(self) -> Path:
        return self.report_dir / "format_comparison.csv"

    @property
    def error_taxonomy_csv(self) -> Path:
        return self.report_dir / "error_taxonomy.csv"

    @property
    def cost_report_csv(self) -> Path:
        return self.report_dir / "cost_report.csv"

    @property
    def primary_results_csv(self) -> Path:
        return self.report_dir / "primary_results.csv"

    @property
    def charts_dir(self) -> Path:
        return self.report_dir / "charts"

    @property
    def learnings_md(self) -> Path:
        return self.report_dir / "LEARNINGS.md"

    @property
    def changes_from_prev_md(self) -> Path:
        suffix = self.previous_version or "previous"
        return self.report_dir / f"CHANGES_FROM_{suffix}.md"

    @property
    def diff_vs_prev_md(self) -> Path:
        suffix = self.previous_version or "previous"
        return self.report_dir / f"DIFF_VS_{suffix}.md"


def make_layout(
    *,
    run_slug: str,
    report_slug: str | None = None,
    version: str | None = None,
    previous_version: str | None = None,
    benchmark_name: str = "datetime_bench",
) -> RunLayout:
    resolved_report_slug = report_slug or run_slug
    return RunLayout(
        benchmark_name=benchmark_name,
        run_root=BENCH_ROOT / "runs" / run_slug,
        report_dir=BENCH_ROOT / "reports" / resolved_report_slug,
        version=version,
        previous_version=previous_version,
        run_slug=run_slug,
        report_slug=resolved_report_slug,
    )


def resolve_layout(
    *,
    run_root: Path,
    report_dir: Path,
    version: str | None = None,
    previous_version: str | None = None,
    benchmark_name: str = "datetime_bench",
) -> RunLayout:
    return RunLayout(
        benchmark_name=benchmark_name,
        run_root=run_root,
        report_dir=report_dir,
        version=version,
        previous_version=previous_version,
        run_slug=run_root.name,
        report_slug=report_dir.name,
    )


def timestamp_utc() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def current_git_sha() -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except Exception:
        return None
    return result.stdout.strip() or None


def build_run_manifest(
    *,
    layout: RunLayout,
    seed: int,
    tasks_path: Path,
    task_count: int,
    format_specs: dict[str, dict[str, str]],
    model_cells: list[dict[str, Any]],
    max_tokens: int,
    temperature: float,
    request_delay_seconds: float,
    max_concurrency: int,
    soft_cap_usd: float,
    hard_cap_usd: float,
    resume: bool,
    selected_models: list[dict[str, Any]] | None = None,
    dry_run_cached: bool = False,
    status: str = "initialized",
    dry_run_path: Path | None = None,
    run_summary_path: Path | None = None,
) -> dict[str, Any]:
    return {
        "benchmark_name": layout.benchmark_name,
        "version": layout.version,
        "previous_version": layout.previous_version,
        "run_slug": layout.run_slug,
        "report_slug": layout.report_slug,
        "status": status,
        "created_at": timestamp_utc(),
        "git_sha": current_git_sha(),
        "seed": seed,
        "resume": resume,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "request_delay_seconds": request_delay_seconds,
        "max_concurrency": max_concurrency,
        "soft_cap_usd": soft_cap_usd,
        "hard_cap_usd": hard_cap_usd,
        "tasks_path": str(tasks_path),
        "task_count": task_count,
        "format_keys": sorted(format_specs),
        "model_cells": model_cells,
        "selected_models": selected_models or [],
        "dry_run_cached": dry_run_cached,
        "paths": {
            "run_root": str(layout.run_root),
            "results_dir": str(layout.results_dir),
            "tasks_dir": str(layout.tasks_dir),
            "report_dir": str(layout.report_dir),
            "log_file": str(layout.log_file),
            "model_selection_file": str(layout.model_selection_file),
            "dry_run_file": str(dry_run_path or layout.dry_run_file),
            "run_summary_file": str(run_summary_path or layout.run_summary_file),
            "run_manifest_file": str(layout.run_manifest_file),
            "summary_md": str(layout.summary_md),
            "format_comparison_csv": str(layout.format_comparison_csv),
            "error_taxonomy_csv": str(layout.error_taxonomy_csv),
            "cost_report_csv": str(layout.cost_report_csv),
            "primary_results_csv": str(layout.primary_results_csv),
            "learnings_md": str(layout.learnings_md),
            "changes_from_prev_md": str(layout.changes_from_prev_md),
            "diff_vs_prev_md": str(layout.diff_vs_prev_md),
        },
    }
