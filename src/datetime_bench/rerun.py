# AI-ANCHOR: datetime-bench rerun: relaxed token budget
"""Full benchmark rerun with relaxed token and spend budgets."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from .analysis import run_analysis
from .config import BENCH_ROOT, FORMAT_SPECS, MAX_CONCURRENCY, MODEL_CELLS, REQUEST_DELAY_SECONDS, SEED, TEMPERATURE
from .layout import build_run_manifest, resolve_layout
from .openrouter import OpenRouterClient, serialize_selections
from .runner import (
    configure_logging,
    execute_benchmark,
    load_existing_budget,
    load_or_generate_tasks,
    resolve_setup,
    write_run_manifest,
)

RERUN_ROOT = BENCH_ROOT / "runs" / "datetime_bench_max2500"
RERUN_RESULTS_DIR = RERUN_ROOT / "results"
RERUN_REPORTS_DIR = BENCH_ROOT / "reports" / "datetime_bench_max2500"
RERUN_LOG_FILE = RERUN_ROOT / "datetime-bench.log"
RERUN_MODEL_SELECTION = RERUN_ROOT / "model_selection.json"
RERUN_DRY_RUN = RERUN_ROOT / "dry_run.json"
RERUN_SUMMARY = RERUN_ROOT / "run_summary.json"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tasks", type=Path, default=None, help="Path to generated tasks JSON")
    parser.add_argument("--results-dir", type=Path, default=RERUN_RESULTS_DIR)
    parser.add_argument("--report-dir", type=Path, default=RERUN_REPORTS_DIR)
    parser.add_argument("--run-root", type=Path, default=RERUN_ROOT)
    parser.add_argument("--seed", type=int, default=SEED)
    parser.add_argument("--max-tokens", type=int, default=2500)
    parser.add_argument("--soft-cap", type=float, default=450.0)
    parser.add_argument("--hard-cap", type=float, default=500.0)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--bench-version", type=str, default="v0.1.5")
    parser.add_argument("--previous-version", type=str, default="v0.1")
    parser.add_argument("--refresh-setup", action="store_true")
    parser.add_argument("--resume", dest="resume", action="store_true", default=True)
    parser.add_argument("--no-resume", dest="resume", action="store_false")
    return parser.parse_args(argv)


async def main_async(args: argparse.Namespace) -> int:
    layout = resolve_layout(
        run_root=args.run_root,
        report_dir=args.report_dir,
        version=args.bench_version,
        previous_version=args.previous_version,
    )
    args.run_root.mkdir(parents=True, exist_ok=True)
    args.results_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    configure_logging(layout.log_file)

    tasks = load_or_generate_tasks(args.tasks or Path(), seed=args.seed) if args.tasks else load_or_generate_tasks(
        BENCH_ROOT / "runs" / "datetime_bench" / "tasks" / f"tasks_seed{args.seed}.json",
        seed=args.seed,
    )

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
                tasks_path=args.tasks or BENCH_ROOT / "runs" / "datetime_bench" / "tasks" / f"tasks_seed{args.seed}.json",
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
                tasks_path=args.tasks or BENCH_ROOT / "runs" / "datetime_bench" / "tasks" / f"tasks_seed{args.seed}.json",
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
        run_analysis(
            results_dir=args.results_dir,
            output_dir=args.report_dir,
            selections=serialize_selections(selections),
            run_summary=run_summary,
            run_manifest=json.loads(layout.run_manifest_file.read_text(encoding="utf-8")),
        )
        return 0
    finally:
        await client.close()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    return asyncio.run(main_async(args))
if __name__ == "__main__":
    raise SystemExit(main())
