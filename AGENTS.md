# datetime-bench Project Notes (quick report)

## Purpose
- `datetime-bench` is a Python benchmark package that measures how reliably LLMs produce datetime strings across multiple formats under zero-shot prompting.
- It targets OpenRouter-hosted models and compares string-format generation behavior across model families, sizes, and reasoning modes.
- Core research question: which format is the most reliable for first-attempt machine parsing and how model behavior changes by task type.

## Current scope (v0.2 design)
- 7 output formats: `iso_8601`, `rfc_3339`, `rfc_2822`, `python_datetime`, `javascript_date`, `natural_language`, `unix_epoch`.
- 7 task generators, 235 total scenarios:
  - `direct_generation` (35)
  - `temporal_arithmetic` (40)
  - `multi_hop_reasoning` (35)
  - `format_conversion` (35)
  - `extraction_from_passage` (30)
  - `edge_cases` (35)
  - `multiple_choice_validation` (25)
- Each scenario is expanded across all 7 formats => 1,645 cases per active model cell.
- 24-cell model matrix in `src/datetime_bench/config.py` (`MODEL_CELLS`) spanning Google, Anthropic, OpenAI, Qwen, GLM with non-reasoning + reasoning variants.

## Workflow at a glance
1. Generate or load tasks:
   - `src/datetime_bench/tasks` creates scenario objects (`TaskScenario`) and expands them into `PromptCase`s.
2. Resolve model cells + dry-run:
   - `runner.resolve_setup()` fetches OpenRouter catalog, probes candidates, estimates per-call cost.
3. Execute benchmark:
   - `runner.execute_benchmark()` batches cells, enforces provider-level rate limiting, runs all cases via async workers, and records per-case JSONL rows.
4. Evaluate responses:
   - `openrouter` performs API calls.
   - `evaluation.parse_output()` normalizes + parses by target format.
   - `evaluation.evaluate_case()` computes correctness + taxonomy metrics.
5. Aggregate reporting:
   - `analysis.run_analysis()` writes summary CSVs and Markdown under `reports/`.

## Runtime artifacts
- Runs are stored under `runs/datetime_bench_v0.2`.
- Reports are under `reports/datetime_bench_v0.2`.
- Key files:
  - `runs/.../model_selection.json`
  - `runs/.../dry_run.json`
  - `runs/.../run_summary.json`
  - `runs/.../results/*.jsonl`
  - `reports/.../*.csv`
  - `reports/.../summary.md`

## CLI entry points
- `datetime-bench` → `src/datetime_bench/runner.py:main`
- `datetime-bench-rerun` → `src/datetime_bench/rerun.py:main` (relaxed budgets + max tokens variant)
- `datetime-bench-few-shot` → `src/datetime_bench/few_shot.py:main` (few-shot extension on selected formats/cells)
- `datetime-bench-rescore` → `src/datetime_bench/rescore.py:main` (recompute scoring/parsing over existing rows)

## Practical notes for contributors
- Requires `OPENROUTER_API_KEY`.
- Budget controls:
  - `SOFT_BUDGET_CAP_USD` and `HARD_BUDGET_CAP_USD` in `config.py`.
  - Soft cap marks remaining cells as skipped; hard cap stops execution.
- `load_or_generate_tasks` persists generated tasks per-seed under the run task directory.
- `FORMAT_SPECS` in `formats.py` drives prompt text + expected pattern examples used for every case.

## Quick project risk notes
- `runner.run_model_cases` reads the same results file inside `log`-like conditionals; avoid relying on that path for strict accounting logic.
- `analysis.py` imports `scipy` if present, but has fallback chi-square logic when unavailable.
- Multiple experimental entry points (`rerun`, `few_shot`) duplicate some orchestration; keep behavior aligned with `runner` if changing output schema.
