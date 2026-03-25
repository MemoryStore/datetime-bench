# AI-ANCHOR: datetime-bench extension: few-shot rerun
"""Few-shot extension for the datetime format benchmark."""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
from collections import defaultdict
from pathlib import Path
from typing import Any

from .analysis import load_results, load_selections, run_analysis
from .config import BENCH_ROOT, REQUEST_DELAY_SECONDS, SEED
from .evaluation import BudgetTracker
from .layout import timestamp_utc
from .openrouter import OpenRouterClient, RateLimiter, serialize_selections
from .rerun import RERUN_MODEL_SELECTION, RERUN_RESULTS_DIR
from .runner import (
    append_result,
    configure_logging,
    execute_case,
    load_completed_case_ids,
    load_or_generate_tasks,
)
from .tasks import build_cases, default_tasks_path, generate_all_tasks
from .tasks.base import FORMAT_KEYS
from .types import PromptCase, SelectedModel

EXTENSION_RUN_ROOT = BENCH_ROOT / "runs" / "datetime_bench_few_shot_max2500"
EXTENSION_RESULTS_DIR = EXTENSION_RUN_ROOT / "results"
EXTENSION_REPORTS_DIR = BENCH_ROOT / "reports" / "datetime_bench_few_shot_max2500"
EXTENSION_RUN_SUMMARY = EXTENSION_RUN_ROOT / "run_summary.json"
EXTENSION_SELECTION_SNAPSHOT = EXTENSION_RUN_ROOT / "model_selection.json"
COMPARISON_CSV = EXTENSION_REPORTS_DIR / "comparison.csv"
COMPARISON_MD = EXTENSION_REPORTS_DIR / "comparison.md"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=None, help="Path to generated tasks JSON")
    parser.add_argument("--results-dir", type=Path, default=EXTENSION_RESULTS_DIR)
    parser.add_argument("--report-dir", type=Path, default=EXTENSION_REPORTS_DIR)
    parser.add_argument(
        "--baseline-results-dir",
        type=Path,
        default=RERUN_RESULTS_DIR,
        help="Zero-shot baseline results to compare against. Defaults to the relaxed max_tokens=2500 rerun.",
    )
    parser.add_argument(
        "--selection-file",
        type=Path,
        default=RERUN_MODEL_SELECTION,
        help="Model selection snapshot to reuse. Defaults to the relaxed max_tokens=2500 rerun.",
    )
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--max-tokens", type=int, default=2500)
    parser.add_argument("--few-shot-count", type=int, default=3)
    parser.add_argument("--soft-cap", type=float, default=450.0)
    parser.add_argument("--hard-cap", type=float, default=500.0)
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    parser.add_argument(
        "--formats",
        nargs="*",
        choices=FORMAT_KEYS,
        default=None,
        help="Override the extension target formats. Defaults to the tied worst baseline formats.",
    )
    return parser.parse_args(argv)


async def main_async(args: argparse.Namespace) -> int:
    run_root = args.results_dir.parent
    run_summary_path = run_root / "run_summary.json"
    selection_snapshot_path = run_root / "model_selection.json"
    log_file = run_root / "datetime-bench.log"

    configure_logging(log_file)
    run_root.mkdir(parents=True, exist_ok=True)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    tasks_path = args.tasks or default_tasks_path(seed=args.seed)
    tasks = load_or_generate_tasks(tasks_path, seed=args.seed)

    baseline_rows = load_results(args.baseline_results_dir)
    target_formats = args.formats or _lowest_performing_formats(baseline_rows)
    selections_payload = load_selections(args.selection_file)
    selections = [SelectedModel(**item) for item in selections_payload if item.get("selected_model")]
    if not selections:
        raise RuntimeError("No baseline model selection found. Run the core benchmark first.")

    exemplar_tasks = generate_all_tasks(seed=args.seed + 1000)
    exemplar_pool = _build_exemplar_pool(exemplar_tasks, few_shot_count=args.few_shot_count)

    client = OpenRouterClient(max_tokens=args.max_tokens)
    budget = BudgetTracker(soft_cap_usd=args.soft_cap, hard_cap_usd=args.hard_cap)
    try:
        await _run_extension(
            client=client,
            tasks=tasks,
            selections=selections,
            exemplar_pool=exemplar_pool,
            target_formats=target_formats,
            results_dir=args.results_dir,
            budget=budget,
            seed=args.seed,
            resume=args.resume,
        )
    finally:
        await client.close()

    run_summary = {
        "timestamp": timestamp_utc(),
        "target_formats": target_formats,
        "few_shot_count": args.few_shot_count,
        "max_tokens": args.max_tokens,
        "budget": budget.summary(),
    }
    run_summary_path.write_text(json.dumps(run_summary, indent=2), encoding="utf-8")
    selection_snapshot_path.write_text(json.dumps(serialize_selections(selections), indent=2), encoding="utf-8")

    report = run_analysis(
        results_dir=args.results_dir,
        output_dir=args.report_dir,
        selections=serialize_selections(selections),
        run_summary=run_summary,
    )
    _write_comparison_reports(
        baseline_rows=baseline_rows,
        extension_rows=load_results(args.results_dir),
        target_formats=target_formats,
        report_dir=args.report_dir,
        max_tokens=args.max_tokens,
        few_shot_count=args.few_shot_count,
        baseline_results_dir=args.baseline_results_dir,
    )
    print(report["summary_md"])
    return 0


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return asyncio.run(main_async(args))


async def _run_extension(
    *,
    client: OpenRouterClient,
    tasks,
    selections: list[SelectedModel],
    exemplar_pool: dict[tuple[str, str], list[PromptCase]],
    target_formats: list[str],
    results_dir: Path,
    budget: BudgetTracker,
    seed: int,
    resume: bool,
) -> None:
    # Extension flow is intentionally selective: only target formats are rewritten
    # with few-shot exemplars, keeping comparisons focused on weakest baseline formats.
    ordered_models = sorted(selections, key=lambda item: item.estimated_unit_cost())
    rate_limiter = RateLimiter(REQUEST_DELAY_SECONDS)
    for index, selection in enumerate(ordered_models, start=1):
        if budget.should_stop_all():
            break
        cases = [
            _with_few_shot_prompt(case, exemplar_pool, target_formats)
            for case in build_cases(tasks, seed=seed + index)
            if case.format_key in target_formats
        ]
        results_path = results_dir / f"{selection.cell}.jsonl"
        completed = load_completed_case_ids(results_path) if resume else set()
        pending_cases = [case for case in cases if case.case_id not in completed]
        if not pending_cases:
            continue
        for case in pending_cases:
            if budget.should_stop_all():
                return
            result = await execute_case(client, selection, case, rate_limiter)
            result["prompt_mode"] = f"few_shot_{case.metadata.get('few_shot_count', 0)}"
            result["max_tokens"] = client.max_tokens
            result["few_shot_examples"] = case.metadata.get("few_shot_example_ids")
            append_result(results_path, result)
            budget.record(
                model_cell=selection.cell,
                task_type=case.task_type,
                cost_usd=float(result.get("estimated_cost_usd") or 0.0),
            )


def _lowest_performing_formats(rows: list[dict[str, Any]]) -> list[str]:
    # Target format selection matches the benchmark metric: semantic correctness rate.
    grouped = defaultdict(lambda: [0, 0])
    for row in rows:
        grouped[row["format"]][0] += 1
        grouped[row["format"]][1] += 1 if row.get("semantic_correct") else 0
    accuracies = {
        format_key: (correct / total if total else 0.0)
        for format_key, (total, correct) in grouped.items()
    }
    if not accuracies:
        return ["natural_language"]
    worst_accuracy = min(accuracies.values())
    return sorted(
        [format_key for format_key, accuracy in accuracies.items() if abs(accuracy - worst_accuracy) < 1e-12]
    )


def _build_exemplar_pool(tasks, *, few_shot_count: int) -> dict[tuple[str, str], list[PromptCase]]:
    pool = defaultdict(list)
    for case in build_cases(tasks, seed=SEED + 1000):
        key = (case.task_type, case.format_key)
        if len(pool[key]) < few_shot_count:
            pool[key].append(case)
    return dict(pool)


def _with_few_shot_prompt(
    case: PromptCase,
    exemplar_pool: dict[tuple[str, str], list[PromptCase]],
    target_formats: list[str],
) -> PromptCase:
    if case.format_key not in target_formats:
        return case
    examples = exemplar_pool.get((case.task_type, case.format_key), [])
    prompt = _render_few_shot_prompt(case, examples)
    return PromptCase(
        case_id=case.case_id,
        task_id=case.task_id,
        task_type=case.task_type,
        format_key=case.format_key,
        prompt=prompt,
        gold_datetime=case.gold_datetime,
        gold_formatted=case.gold_formatted,
        metadata={
            **case.metadata,
            "few_shot_count": len(examples),
            "few_shot_example_ids": [example.case_id for example in examples],
        },
    )


def _render_few_shot_prompt(case: PromptCase, examples: list[PromptCase]) -> str:
    sections = [
        "Follow the solved examples exactly. Respond with ONLY the final answer, with no explanation.",
        "",
    ]
    for index, example in enumerate(examples, start=1):
        sections.append(f"Example {index}")
        sections.append(example.prompt)
        sections.append(_example_answer(example))
        sections.append("")
    sections.append("Now solve the next task.")
    sections.append(case.prompt)
    return "\n".join(sections).strip()


def _example_answer(example: PromptCase) -> str:
    if example.task_type == "multiple_choice_validation":
        return str(example.metadata.get("correct_choice") or "")
    return example.gold_formatted


def _write_comparison_reports(
    *,
    baseline_rows: list[dict[str, Any]],
    extension_rows: list[dict[str, Any]],
    target_formats: list[str],
    report_dir: Path,
    max_tokens: int,
    few_shot_count: int,
    baseline_results_dir: Path,
) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    comparison_csv = report_dir / COMPARISON_CSV.name
    comparison_md = report_dir / COMPARISON_MD.name
    comparison_rows = []
    for format_key in target_formats:
        baseline_items = [row for row in baseline_rows if row["format"] == format_key]
        extension_items = [row for row in extension_rows if row["format"] == format_key]
        comparison_rows.append(
            {
                "format": format_key,
                "baseline_accuracy": _accuracy(baseline_items),
                "few_shot_accuracy": _accuracy(extension_items),
                "delta": round(_accuracy(extension_items) - _accuracy(baseline_items), 6),
                "baseline_n": len(baseline_items),
                "few_shot_n": len(extension_items),
            }
        )
        baseline_cells = sorted({row["model_cell"] for row in baseline_items})
        for model_cell in baseline_cells:
            baseline_cell_items = [row for row in baseline_items if row["model_cell"] == model_cell]
            extension_cell_items = [row for row in extension_items if row["model_cell"] == model_cell]
            comparison_rows.append(
                {
                    "format": format_key,
                    "model_cell": model_cell,
                    "baseline_accuracy": _accuracy(baseline_cell_items),
                    "few_shot_accuracy": _accuracy(extension_cell_items),
                    "delta": round(_accuracy(extension_cell_items) - _accuracy(baseline_cell_items), 6),
                    "baseline_n": len(baseline_cell_items),
                    "few_shot_n": len(extension_cell_items),
                }
            )
    with comparison_csv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["format", "model_cell", "baseline_accuracy", "few_shot_accuracy", "delta", "baseline_n", "few_shot_n"],
        )
        writer.writeheader()
        writer.writerows(comparison_rows)

    lines = [
        "# Few-Shot Extension Comparison",
        "",
        f"- Target formats: {', '.join(target_formats)}",
        f"- Few-shot examples per prompt: {few_shot_count}",
        f"- Max tokens: {max_tokens}",
        f"- Baseline results: `{baseline_results_dir}`",
        "- Extension uses the same selected model cells and adds task-type-matched few-shot exemplars.",
        "",
        "| Format | Baseline | Few-shot | Delta |",
        "| ------ | -------- | -------- | ----- |",
    ]
    overall_rows = [row for row in comparison_rows if not row.get("model_cell")]
    for row in overall_rows:
        lines.append(
            f"| {row['format']} | {row['baseline_accuracy'] * 100:.2f}% | "
            f"{row['few_shot_accuracy'] * 100:.2f}% | {row['delta'] * 100:+.2f} pts |"
        )
    lines.append("")
    lines.append("| Format | Model Cell | Baseline | Few-shot | Delta |")
    lines.append("| ------ | ---------- | -------- | -------- | ----- |")
    for row in comparison_rows:
        if not row.get("model_cell"):
            continue
        lines.append(
            f"| {row['format']} | {row['model_cell']} | {row['baseline_accuracy'] * 100:.2f}% | "
            f"{row['few_shot_accuracy'] * 100:.2f}% | {row['delta'] * 100:+.2f} pts |"
        )
    comparison_md.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _accuracy(rows: list[dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    return sum(1 for row in rows if row.get("semantic_correct")) / len(rows)


if __name__ == "__main__":
    raise SystemExit(main())
