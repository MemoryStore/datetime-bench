# AI-ANCHOR: datetime-bench: benchmark orchestration CLI
"""Generate tasks, run the OpenRouter benchmark, and write reports."""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import sys
import time
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .analysis import run_analysis
from .config import (
    BENCH_VERSION,
    CELL_PARALLELISM,
    DEFAULT_LAYOUT,
    FORMAT_SPECS,
    HARD_BUDGET_CAP_USD,
    MAX_CONCURRENCY,
    MAX_COMPLETION_TOKENS,
    MODEL_CELLS,
    PREVIOUS_BENCH_VERSION,
    REQUEST_DELAY_SECONDS,
    SEED,
    SOFT_BUDGET_CAP_USD,
    TEMPERATURE,
)
from .evaluation import BudgetTracker, clean_output, evaluate_case, parse_output
from .layout import RunLayout, build_run_manifest, resolve_layout, timestamp_utc
from .openrouter import (
    OpenRouterClient,
    RateLimiter,
    deserialize_selections,
    estimate_cost,
    extract_message_content,
    serialize_selections,
    usage_from_payload,
)
from .tasks import build_cases, default_tasks_path, generate_all_tasks, load_generated_tasks, save_generated_tasks
from .types import PromptCase, SelectedModel

LOGGER = logging.getLogger("benchmarks.datetime_bench")


def configure_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    root = logging.getLogger()
    root.setLevel(logging.DEBUG)
    for handler in list(root.handlers):
        root.removeHandler(handler)
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.INFO)
    console.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s", "%H:%M:%S"))
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s", "%Y-%m-%d %H:%M:%S")
    )
    root.addHandler(console)
    root.addHandler(file_handler)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=None, help="Path to generated tasks JSON")
    parser.add_argument("--run-root", type=Path, default=DEFAULT_LAYOUT.run_root)
    parser.add_argument("--results-dir", type=Path, default=DEFAULT_LAYOUT.results_dir)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_LAYOUT.report_dir)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--bench-version", type=str, default=BENCH_VERSION)
    parser.add_argument("--previous-version", type=str, default=PREVIOUS_BENCH_VERSION)
    parser.add_argument("--max-tokens", type=int, default=MAX_COMPLETION_TOKENS)
    parser.add_argument("--soft-cap", type=float, default=SOFT_BUDGET_CAP_USD)
    parser.add_argument("--hard-cap", type=float, default=HARD_BUDGET_CAP_USD)
    parser.add_argument("--dry-run", action="store_true", help="Run setup validation and cost estimation first")
    parser.add_argument("--no-confirm", action="store_true", help="Auto-proceed after dry run")
    parser.add_argument(
        "--refresh-setup",
        action="store_true",
        help="Ignore cached model selection and dry-run snapshots when resuming a run",
    )
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument("--skip-analysis", action="store_true")
    return parser.parse_args(argv)


async def main_async(args: argparse.Namespace) -> int:
    layout = resolve_layout(
        run_root=args.run_root,
        report_dir=args.report_dir,
        version=args.bench_version,
        previous_version=args.previous_version,
    )
    configure_logging(layout.log_file)
    layout.run_root.mkdir(parents=True, exist_ok=True)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    tasks_path = args.tasks or default_tasks_path(seed=args.seed, tasks_dir=layout.tasks_dir)
    tasks = load_or_generate_tasks(tasks_path, seed=args.seed)

    client = OpenRouterClient(max_tokens=args.max_tokens)
    try:
        selections, _probe_report, used_cached_setup = await resolve_setup(
            client=client,
            tasks=tasks,
            layout=layout,
            resume=args.resume,
            refresh_setup=args.refresh_setup,
        )
        write_run_manifest(
            layout,
            build_run_manifest(
                layout=layout,
                seed=args.seed,
                tasks_path=tasks_path,
                task_count=len(tasks),
                format_specs=FORMAT_SPECS,
                model_cells=[cell.__dict__ for cell in MODEL_CELLS],
                max_tokens=args.max_tokens,
                temperature=TEMPERATURE,
                request_delay_seconds=REQUEST_DELAY_SECONDS,
                max_concurrency=MAX_CONCURRENCY,
                soft_cap_usd=args.soft_cap,
                hard_cap_usd=args.hard_cap,
                resume=args.resume,
                selected_models=serialize_selections(selections),
                dry_run_cached=used_cached_setup,
                status="ready" if args.dry_run else "running",
            ),
        )

        if args.dry_run:
            if not should_proceed_after_dry_run(args.no_confirm):
                LOGGER.info("Dry run complete; stopping before full benchmark.")
                return 0

        budget = load_existing_budget(args.results_dir, soft_cap_usd=args.soft_cap, hard_cap_usd=args.hard_cap)
        run_summary = await execute_benchmark(
            client=client,
            tasks=tasks,
            selections=selections,
            results_dir=args.results_dir,
            budget=budget,
            seed=args.seed,
            resume=args.resume,
        )
        run_summary["max_tokens"] = args.max_tokens
        run_summary["soft_cap_usd"] = args.soft_cap
        run_summary["hard_cap_usd"] = args.hard_cap
        layout.run_summary_file.write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
        write_run_manifest(
            layout,
            build_run_manifest(
                layout=layout,
                seed=args.seed,
                tasks_path=tasks_path,
                task_count=len(tasks),
                format_specs=FORMAT_SPECS,
                model_cells=[cell.__dict__ for cell in MODEL_CELLS],
                max_tokens=args.max_tokens,
                temperature=TEMPERATURE,
                request_delay_seconds=REQUEST_DELAY_SECONDS,
                max_concurrency=MAX_CONCURRENCY,
                soft_cap_usd=args.soft_cap,
                hard_cap_usd=args.hard_cap,
                resume=args.resume,
                selected_models=serialize_selections(selections),
                dry_run_cached=used_cached_setup,
                status="complete",
                run_summary_path=layout.run_summary_file,
            ),
        )
        if not args.skip_analysis:
            analysis_report = run_analysis(
                results_dir=args.results_dir,
                output_dir=args.report_dir,
                selections=serialize_selections(selections),
                run_summary=run_summary,
                run_manifest=json.loads(layout.run_manifest_file.read_text(encoding="utf-8")),
            )
            LOGGER.info("Analysis written to %s", analysis_report["summary_md"])
        return 0
    finally:
        await client.close()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return asyncio.run(main_async(args))


def load_or_generate_tasks(path: Path, seed: int = SEED):
    if path.exists():
        LOGGER.info("Loading generated tasks from %s", path)
        return load_generated_tasks(path)
    tasks = generate_all_tasks(seed=seed)
    save_generated_tasks(tasks, path=path)
    LOGGER.info("Generated %s tasks at %s", len(tasks), path)
    return tasks


async def resolve_setup(
    *,
    client: OpenRouterClient,
    tasks,
    layout: RunLayout,
    resume: bool,
    refresh_setup: bool,
) -> tuple[list[SelectedModel], dict[str, Any], bool]:
    if resume and not refresh_setup and layout.model_selection_file.exists() and layout.dry_run_file.exists():
        LOGGER.info("Reusing cached model selection and dry-run snapshots from %s", layout.run_root)
        selections = deserialize_selections(json.loads(layout.model_selection_file.read_text(encoding="utf-8")))
        probe_report = json.loads(layout.dry_run_file.read_text(encoding="utf-8"))
        return selections, probe_report, True

    selections = await client.select_models()
    probe_report = await run_dry_run_checks(client, tasks, selections)
    layout.model_selection_file.write_text(json.dumps(serialize_selections(selections), indent=2), encoding="utf-8")
    layout.dry_run_file.write_text(json.dumps(probe_report, indent=2), encoding="utf-8")
    return selections, probe_report, False


def write_run_manifest(layout: RunLayout, manifest: dict[str, Any]) -> None:
    layout.run_manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


async def run_dry_run_checks(
    client: OpenRouterClient,
    tasks,
    selections: list[SelectedModel],
) -> dict[str, Any]:
    LOGGER.info("Dry run: generated %s tasks", len(tasks))
    examples = _task_examples(tasks)
    for task_type, sample_rows in examples.items():
        LOGGER.info("Dry run examples for %s:", task_type)
        for sample in sample_rows:
            LOGGER.info("  %s", sample)

    roundtrip = _parser_roundtrip_check(tasks[0].gold_datetime)
    LOGGER.info("Parser round-trip sample: %s", roundtrip)

    probe_results: list[dict[str, Any]] = []
    trivial_case = PromptCase(
        case_id="dry_run_probe__iso_8601",
        task_id="dry_run_probe",
        task_type="direct_generation",
        format_key="iso_8601",
        prompt=(
            "Convert March 15, 2025 at 12:00 PM in timezone UTC to ISO 8601.\n\n"
            "Output format: ISO 8601\n"
            "Expected format pattern: YYYY-MM-DDTHH:MM:SS±HH:MM\n"
            "Example of this format: 2025-01-15T09:30:00-05:00\n\n"
            "Your answer:"
        ),
        gold_datetime=datetime(2025, 3, 15, 12, 0, tzinfo=UTC),
        gold_formatted="2025-03-15T12:00:00+00:00",
        metadata={},
    )
    stress_probe_cases = _stress_probe_cases(tasks)
    for selection in selections:
        if not selection.selected_model:
            probe_results.append({"cell": selection.cell, "status": "skipped", "reason": selection.notes})
            continue
        probe_cases = [trivial_case]
        if selection.reasoning_mode == "reasoning":
            probe_cases.extend(stress_probe_cases)
        probe_record = await _probe_selection(client, selection, probe_cases)
        probe_results.append(probe_record)
    planned_calls_per_model = len(build_cases(tasks, seed=SEED))
    estimated_total_cost = 0.0
    for item in probe_results:
        if item.get("status") == "ok":
            estimated_total_cost += float(item["unit_estimated_cost_usd"]) * planned_calls_per_model
    LOGGER.info(
        "Dry run estimated total benchmark cost: $%.4f for %s calls/model",
        estimated_total_cost,
        planned_calls_per_model,
    )
    return {
        "generated_task_count": len(tasks),
        "examples": examples,
        "parser_roundtrip": roundtrip,
        "stress_probe_case_ids": [case.case_id for case in stress_probe_cases],
        "probe_results": probe_results,
        "planned_calls_per_model": planned_calls_per_model,
        "estimated_total_cost_usd": round(estimated_total_cost, 6),
    }


def _provider_key(model_id: str) -> str:
    """Extract provider from model slug (e.g., 'google/gemini-3.1-pro' -> 'google')."""
    return model_id.split("/")[0] if "/" in model_id else "unknown"


def _build_batches(
    models: list[SelectedModel],
    max_per_batch: int,
) -> list[list[tuple[int, SelectedModel]]]:
    """Group models into batches, spreading providers evenly.

    Fills each batch up to *max_per_batch* cells.  Within a batch,
    providers are interleaved (round-robin) so the per-provider rate
    limiters distribute load naturally.  Multiple cells from the same
    provider are allowed in the same batch — the rate limiter handles
    contention.
    """
    remaining = list(enumerate(models, start=1))
    batches: list[list[tuple[int, SelectedModel]]] = []
    while remaining:
        batch = remaining[:max_per_batch]
        remaining = remaining[max_per_batch:]
        batches.append(batch)
    return batches


async def execute_benchmark(
    *,
    client: OpenRouterClient,
    tasks,
    selections: list[SelectedModel],
    results_dir: Path,
    budget: BudgetTracker,
    seed: int,
    resume: bool,
) -> dict[str, Any]:
    # One rate limiter per provider to respect per-provider limits
    provider_limiters: dict[str, RateLimiter] = {}
    ordered_models = sorted(
        [selection for selection in selections if selection.selected_model],
        key=lambda item: item.estimated_unit_cost(),
    )
    for sel in ordered_models:
        pkey = _provider_key(sel.selected_model or "")
        if pkey not in provider_limiters:
            provider_limiters[pkey] = RateLimiter(REQUEST_DELAY_SECONDS)

    batches = _build_batches(ordered_models, CELL_PARALLELISM)
    skipped_cells: list[dict[str, str]] = []

    LOGGER.info(
        "Executing %s model cells in %s batches (max %s concurrent)",
        len(ordered_models),
        len(batches),
        CELL_PARALLELISM,
    )

    for batch_idx, batch in enumerate(batches, start=1):
        if budget.should_stop_all():
            for _, sel in batch:
                skipped_cells.append({"cell": sel.cell, "reason": "hard_budget_cap"})
            continue

        runnable = [(idx, sel) for idx, sel in batch if not budget.soft_cap_triggered]
        for _, sel in batch:
            if budget.soft_cap_triggered:
                skipped_cells.append({"cell": sel.cell, "reason": "soft_budget_cap"})

        if not runnable:
            continue

        LOGGER.info(
            "Batch %s/%s: running %s cells concurrently (%s)",
            batch_idx,
            len(batches),
            len(runnable),
            ", ".join(sel.cell for _, sel in runnable),
        )

        async def _run_cell(cell_index: int, selection: SelectedModel) -> None:
            cases = build_cases(tasks, seed=seed + cell_index)
            results_path = results_dir / f"{selection.cell}.jsonl"
            completed = load_completed_case_ids(results_path) if resume else set()
            pending = [c for c in cases if c.case_id not in completed]
            LOGGER.info(
                "  %s (%s): %s pending, %s resumed",
                selection.cell,
                selection.selected_model,
                len(pending),
                len(completed),
            )
            if not pending:
                return
            limiter = provider_limiters[_provider_key(selection.selected_model or "")]
            await run_model_cases(
                client=client,
                model=selection,
                cases=pending,
                results_path=results_path,
                budget=budget,
                rate_limiter=limiter,
            )

        await asyncio.gather(*[_run_cell(idx, sel) for idx, sel in runnable])

    summary = {
        "budget": budget.summary(),
        "skipped_cells": skipped_cells,
        "timestamp": timestamp_utc(),
    }
    return summary


async def run_model_cases(
    *,
    client: OpenRouterClient,
    model: SelectedModel,
    cases: list[PromptCase],
    results_path: Path,
    budget: BudgetTracker,
    rate_limiter: RateLimiter,
) -> None:
    queue: asyncio.Queue[PromptCase] = asyncio.Queue()
    for case in cases:
        queue.put_nowait(case)
    write_lock = asyncio.Lock()

    async def worker() -> None:
        while not queue.empty():
            if budget.should_stop_all() or budget.soft_cap_triggered:
                return
            try:
                case = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            result = await execute_case(client, model, case, rate_limiter)
            budget.record(
                model_cell=model.cell,
                task_type=case.task_type,
                cost_usd=float(result.get("estimated_cost_usd") or 0.0),
            )
            async with write_lock:
                append_result(results_path, result)
            LOGGER.info(
                "%s %s %s %s",
                case.task_id,
                model.cell,
                case.format_key,
                "correct" if result.get("semantic_correct") else "incorrect",
            )
            if budget.total_spend_usd and int(sum(1 for _ in open(results_path, encoding='utf-8'))) % 100 == 0:
                LOGGER.info("Cumulative spend after %s: $%.4f", model.cell, budget.total_spend_usd)
            queue.task_done()

    workers = [asyncio.create_task(worker()) for _ in range(min(MAX_CONCURRENCY, len(cases)))]
    await asyncio.gather(*workers)


async def execute_case(
    client: OpenRouterClient,
    model: SelectedModel,
    case: PromptCase,
    rate_limiter: RateLimiter,
) -> dict[str, Any]:
    started = time.perf_counter()
    try:
        await rate_limiter.wait()
        payload = await client.complete_case(model, case)
        latency_ms = int(1000 * (time.perf_counter() - started))
        raw_output = extract_message_content(payload)
        cleaned = clean_output(raw_output)
        parse_result = parse_output(case, cleaned)
        evaluation = evaluate_case(case, raw_output, parse_result)
        usage = usage_from_payload(payload)
        estimated_cost = estimate_cost(usage, model.pricing)
        return {
            "case_id": case.case_id,
            "task_id": case.task_id,
            "task_type": case.task_type,
            "format": case.format_key,
            "model": model.selected_model,
            "provider_model": payload.get("model") or model.selected_model,
            "model_cell": model.cell,
            "reasoning_mode": model.reasoning_mode,
            "raw_output": raw_output,
            "cleaned_output": parse_result.cleaned_output,
            "gold_formatted": case.gold_formatted,
            "gold_choice": case.metadata.get("correct_choice"),
            "options": case.metadata.get("options"),
            "syntactic_valid": evaluation.syntactic_valid,
            "semantic_correct": evaluation.semantic_correct,
            "strict_correct": evaluation.strict_correct,
            "calendar_consistent": evaluation.calendar_consistent,
            "format_compliance": evaluation.format_compliance,
            "extraction_clean": evaluation.extraction_clean,
            "latency_ms": latency_ms,
            "input_tokens": usage.get("prompt_tokens"),
            "output_tokens": usage.get("completion_tokens"),
            "reasoning_tokens": usage.get("reasoning_tokens"),
            "estimated_cost_usd": round(estimated_cost, 8),
            "timestamp": timestamp_utc(),
            "error": None,
            "error_type": evaluation.error_type,
            "error_subtype": evaluation.error_subtype,
            "delta_seconds": evaluation.delta_seconds,
            "parse_mode": evaluation.parse_mode,
            "warnings": evaluation.warnings,
            "selected_choice": evaluation.selected_choice,
            "selected_option_content": evaluation.selected_option_content,
        }
    except Exception as exc:
        latency_ms = int(1000 * (time.perf_counter() - started))
        return {
            "case_id": case.case_id,
            "task_id": case.task_id,
            "task_type": case.task_type,
            "format": case.format_key,
            "model": model.selected_model,
            "provider_model": model.selected_model,
            "model_cell": model.cell,
            "reasoning_mode": model.reasoning_mode,
            "raw_output": "",
            "cleaned_output": "",
            "gold_formatted": case.gold_formatted,
            "gold_choice": case.metadata.get("correct_choice"),
            "options": case.metadata.get("options"),
            "syntactic_valid": False,
            "semantic_correct": False,
            "strict_correct": False,
            "calendar_consistent": None,
            "format_compliance": 0.0,
            "extraction_clean": True,
            "latency_ms": latency_ms,
            "input_tokens": 0,
            "output_tokens": 0,
            "reasoning_tokens": 0,
            "estimated_cost_usd": 0.0,
            "timestamp": timestamp_utc(),
            "error": f"{type(exc).__name__}: {exc}",
            "error_type": "api_error",
            "error_subtype": None,
            "delta_seconds": None,
            "parse_mode": None,
            "warnings": [],
            "selected_choice": None,
            "selected_option_content": None,
        }


def load_completed_case_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    completed: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                completed.add(json.loads(line)["case_id"])
    return completed


def load_existing_budget(
    results_dir: Path,
    *,
    soft_cap_usd: float = SOFT_BUDGET_CAP_USD,
    hard_cap_usd: float = HARD_BUDGET_CAP_USD,
) -> BudgetTracker:
    budget = BudgetTracker(soft_cap_usd=soft_cap_usd, hard_cap_usd=hard_cap_usd)
    if not results_dir.exists():
        return budget
    for path in results_dir.glob("*.jsonl"):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                row = json.loads(line)
                budget.record(
                    model_cell=row.get("model_cell") or "unknown",
                    task_type=row.get("task_type") or "unknown",
                    cost_usd=float(row.get("estimated_cost_usd") or 0.0),
                )
    return budget


def append_result(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(result, ensure_ascii=False) + "\n")


def should_proceed_after_dry_run(no_confirm: bool) -> bool:
    if no_confirm:
        return True
    if not sys.stdin.isatty():
        return False
    response = input("Proceed with the full benchmark? [y/N] ").strip().lower()
    return response in {"y", "yes"}


def _task_examples(tasks) -> dict[str, list[str]]:
    grouped: dict[str, list[str]] = defaultdict(list)
    for task in tasks:
        samples = grouped[task.task_type]
        if len(samples) >= 3:
            continue
        fmt = next(iter(task.instruction_by_format))
        samples.append(task.instruction_by_format[fmt])
    return dict(grouped)


def _parser_roundtrip_check(sample_dt: datetime) -> dict[str, bool]:
    from .formats import format_datetime
    from .tasks.base import FORMAT_KEYS

    results = {}
    for format_key in FORMAT_KEYS:
        formatted = format_datetime(sample_dt, format_key)
        case = PromptCase(
            case_id=f"roundtrip__{format_key}",
            task_id="roundtrip",
            task_type="direct_generation",
            format_key=format_key,
            prompt="",
            gold_datetime=sample_dt,
            gold_formatted=formatted,
            metadata={},
        )
        parsed = parse_output(case, formatted)
        results[format_key] = parsed.syntactic_valid
    return results


def _stress_probe_cases(tasks) -> list[PromptCase]:
    # AI-NOTE: Reasoning cells need representative prompts because some providers
    # consume the visible output budget on hidden reasoning and pass a trivial probe.
    candidate_cases = build_cases(tasks, seed=SEED)
    targets = (
        ("temporal_arithmetic", "natural_language"),
        ("multi_hop_reasoning", "natural_language"),
        ("extraction_from_passage", "iso_8601"),
    )
    selected: list[PromptCase] = []
    for task_type, format_key in targets:
        match = next(
            (
                case
                for case in candidate_cases
                if case.task_type == task_type and case.format_key == format_key
            ),
            None,
        )
        if match is not None:
            selected.append(match)
    return selected
async def _probe_selection(
    client: OpenRouterClient,
    selection: SelectedModel,
    probe_cases: list[PromptCase],
) -> dict[str, Any]:
    candidates = list(selection.requested_candidates)
    current = selection.selected_model
    if current in candidates:
        candidates = candidates[candidates.index(current) :]
    for candidate in candidates:
        candidate_selection = client.build_candidate_selection(selection, candidate)
        if candidate_selection is None:
            continue
        candidate_probe_results: list[dict[str, Any]] = []
        candidate_probe_costs: list[float] = []
        candidate_failed = False
        for probe_case in probe_cases:
            started = time.perf_counter()
            try:
                payload = await client.complete_case(candidate_selection, probe_case)
                latency_ms = int(1000 * (time.perf_counter() - started))
                raw_output = extract_message_content(payload)
                cleaned = clean_output(raw_output)
                parse_result = parse_output(probe_case, cleaned)
                evaluation = evaluate_case(probe_case, raw_output, parse_result)
                usage = usage_from_payload(payload)
                estimated_cost = estimate_cost(usage, candidate_selection.pricing)
                candidate_probe_costs.append(estimated_cost)
                candidate_probe_results.append(
                    {
                        "case_id": probe_case.case_id,
                        "task_type": probe_case.task_type,
                        "format": probe_case.format_key,
                        "latency_ms": latency_ms,
                        "raw_output": raw_output,
                        "usage": usage,
                        "syntactic_valid": evaluation.syntactic_valid,
                        "semantic_correct": evaluation.semantic_correct,
                    }
                )
                if not evaluation.syntactic_valid:
                    selection.notes.append(
                        "probe_incompatible:"
                        f"{candidate}:{probe_case.case_id}:"
                        f"syntactic={evaluation.syntactic_valid}:semantic={evaluation.semantic_correct}"
                    )
                    candidate_failed = True
                    break
                if not evaluation.semantic_correct:
                    selection.notes.append(
                        f"probe_semantic_warning:{candidate}:{probe_case.case_id}"
                    )
            except Exception as exc:
                selection.notes.append(f"probe_failed:{candidate}:{probe_case.case_id}:{type(exc).__name__}:{exc}")
                candidate_failed = True
                break
        if not candidate_failed:
            selection.selected_model = candidate_selection.selected_model
            selection.pricing = candidate_selection.pricing
            selection.reasoning_config = candidate_selection.reasoning_config
            if candidate != current:
                selection.notes.append(f"probe_fallback:{candidate}")
            unit_estimated_cost = sum(candidate_probe_costs) / len(candidate_probe_costs)
            return {
                "cell": selection.cell,
                "model": selection.selected_model,
                "status": "ok",
                "probe_cases": candidate_probe_results,
                "probe_count": len(candidate_probe_results),
                "probe_cost_total_usd": round(sum(candidate_probe_costs), 8),
                "unit_estimated_cost_usd": round(unit_estimated_cost, 8),
            }
    selection.selected_model = None
    return {
        "cell": selection.cell,
        "model": None,
        "status": "error",
        "error": "no_probe_compatible_candidate",
    }
