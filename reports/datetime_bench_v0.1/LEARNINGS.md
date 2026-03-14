# Datetime Benchmark v0.1 Learnings

## Scope

- Formats: `iso_8601`, `rfc_2822`, `natural_language`
- Cells: 6 (`small/med/large` x `reasoning/non_reasoning`)
- Token ceiling: `2500`
- Total spend: `$7.454499`

## Headline

- `iso_8601` won overall at `92.74%`
- `rfc_2822` landed at `88.57%`
- `natural_language` landed at `86.67%`
- `iso_8601` beat `natural_language` with `p=4.24041e-05`
- `iso_8601` beat `rfc_2822` with `p=0.00334895`

## What We Learned

- `ISO 8601` is the best default for zero-shot timestamp generation.
- `RFC 2822` does not beat ISO overall, despite the natural-language token prior hypothesis.
- Reasoning helped `rfc_2822` much more than the other two formats: `+4.29` points over non-reasoning.
- `direct_generation` was saturated at `100%` across all three formats, so it contributes continuity more than discrimination.
- `format_conversion`, `multi_hop_reasoning`, and `temporal_arithmetic` were the most format-sensitive tasks.
- Arithmetic and weekday computation were the two dominant failure classes.
- Small models were materially worse than medium and large, but the gain was modest relative to cost.

## Error Profile

- `iso_8601`: mostly `arithmetic_error`, then `extraction_error`
- `natural_language`: `arithmetic_error`, `day_of_week_error`, `timezone_error`
- `rfc_2822`: `arithmetic_error`, `day_of_week_error`, `extraction_error`

## Implication For Next Phase

- Keep `iso_8601` as the baseline winner to beat.
- Expand format coverage without changing the task taxonomy yet.
- Preserve this run as the reference point for later diffs.
