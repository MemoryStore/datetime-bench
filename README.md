# datetime-bench

`datetime-bench` is a standalone benchmark for measuring how reliably LLMs generate requested datetime formats.

It was extracted from the Memory Store research harness so the datetime-format work can evolve in public without dragging the rest of the monorepo with it.

## Current recommendation

From the committed `v0.2` baseline, the default machine-facing output target is `RFC 3339`.

`v0.2` headline:
- `rfc_3339`: `90.99%`
- `python_datetime`: `90.85%`
- `iso_8601`: `90.50%`
- `javascript_date`: `86.38%`
- `rfc_2822`: `86.17%`
- `natural_language`: `84.33%`
- `unix_epoch`: `39.86%`

`RFC 3339` is statistically tied with `python_datetime` and `iso_8601`, but it is the recommended default because it is strict, portable, and not runtime-specific.

## Install

```bash
uv sync
```

## Run

```bash
export OPENROUTER_API_KEY="sk-or-..."
datetime-bench --dry-run
datetime-bench
```

The benchmark writes raw artifacts to `runs/` and analysis outputs to `reports/`.

## Repo layout

- `src/datetime_bench/`: benchmark package
- `reports/datetime_bench_v0.1/`: three-format baseline artifacts
- `reports/datetime_bench_v0.1.5/`: six-format expansion artifacts
- `reports/datetime_bench_v0.2/`: current baseline artifacts and the narrative program report

Start with:
- `reports/datetime_bench_v0.2/PROGRAM_REPORT.md`
- `reports/datetime_bench_v0.2/summary.md`

## Notes

This repo keeps the benchmark code and versioned report artifacts. It intentionally does not include the raw `runs/` outputs from the originating monorepo extraction.
