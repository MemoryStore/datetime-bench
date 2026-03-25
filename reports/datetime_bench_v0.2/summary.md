# Datetime Format Benchmark Summary

This file is a published snapshot of the v0.2 headline results.

The raw `runs/datetime_bench_v0.2` artifacts required to regenerate the full auto-generated summary are not included in this source checkout. `analysis.py` now refuses to overwrite reports when result rows are missing, and the interaction breakdown logic has been fixed to use declared model-cell metadata for `size` and `reasoning_mode`.

## Headline Format Comparison

| Format | Accuracy | Strict | 95% CI |
| ------ | -------- | ------ | ------ |
| iso_8601 | 86.83% | 86.83% | 85.9–87.7% |
| python_datetime | 86.52% | 86.52% | 85.6–87.4% |
| rfc_3339 | 86.40% | 86.40% | 85.5–87.3% |
| rfc_2822 | 82.50% | 76.95% | 81.5–83.5% |
| javascript_date | 79.79% | 73.87% | 78.7–80.8% |
| natural_language | 79.29% | 72.78% | 78.2–80.3% |
| unix_epoch | 46.60% | 46.60% | 45.3–47.9% |

## Key Conclusions

- The top cluster is `iso_8601`, `python_datetime`, and `rfc_3339`.
- `rfc_3339` remains the default recommendation for machine-facing prompts because it stays in the top cluster while naming a narrower, more portable spec than broad `iso_8601`.
- Weekday-bearing formats pay a clear strict-scoring penalty: `rfc_2822` `-5.55`, `javascript_date` `-5.92`, `natural_language` `-6.51`.
- `unix_epoch` is not a peer string-format task. It measures numeric conversion ability and should be interpreted separately.

## Canonical Published Sources

- [`README.md`](../../README.md) for the main published narrative
- [`LEARNINGS.md`](./LEARNINGS.md) for the v0.2 synthesis
- [`PROGRAM_REPORT.md`](./PROGRAM_REPORT.md) for the broader program-level report

## Regeneration Note

To rebuild the detailed summary tables and CSVs, restore the missing `runs/datetime_bench_v0.2` result artifacts and rerun the analysis pipeline. Without those raw rows, checked-in narrative documents are the authoritative v0.2 record in this repo.
