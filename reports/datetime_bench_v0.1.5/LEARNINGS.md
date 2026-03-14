# Datetime Benchmark v0.1.5 Learnings

## Scope

- Formats: `iso_8601`, `rfc_3339`, `rfc_2822`, `natural_language`, `javascript_date`, `python_datetime`
- Cells: 6 (`small/med/large` x `reasoning/non_reasoning`)
- Token ceiling: `2500`
- Run namespace: `runs/datetime_bench_six_formats_max2500`
- Total spend: `$15.366276`

## Headline

- `python_datetime` finished first at `93.81%`
- `rfc_3339` finished second at `93.21%`
- `iso_8601` finished third at `92.86%`
- `python_datetime` was not meaningfully different from `iso_8601` (`p=0.433944`)
- `python_datetime` was not meaningfully different from `rfc_3339` (`p=0.620425`)
- Both runtime-native machine forms outperformed `natural_language`

## What We Learned

- The extra formats do not collapse into the original three-format result.
- `python_datetime` is the strongest overall surface form in this run.
- `rfc_3339` is effectively as strong as `iso_8601`, despite the stricter canonical form.
- `javascript_date` is usable, but it pays a real weekday and arithmetic tax.
- `natural_language` remains the weakest of the six.
- `rfc_2822` improved materially under reasoning (`+4.29` points), but still did not catch the top machine-oriented formats.
- Reasoning mattered most for `javascript_date` (`+7.14` points) and `rfc_2822` (`+4.29` points), and barely moved `iso_8601`, `rfc_3339`, or `natural_language`.

## What Changed Relative To v0.1

- The space-separated Python native form outperformed all three original formats.
- Strict `rfc_3339` formatting remained distinct from the broader `iso_8601` bucket, but the two behaved similarly well.
- Runtime-native string forms exposed different failure modes than standards-track formats, especially around weekday tokens and arithmetic.
- The prior headline recommendation of `iso_8601` became too narrow once these two additional machine-oriented formats were added.

## Error Profile

- `python_datetime`: mostly `arithmetic_error`, then `extraction_error`
- `rfc_3339`: mostly `arithmetic_error`, then `extraction_error`
- `iso_8601`: mostly `arithmetic_error`, then `extraction_error`
- `javascript_date`: `arithmetic_error`, `day_of_week_error`, `unknown`
- `natural_language`: `arithmetic_error`, `timezone_error`, `day_of_week_error`
- `rfc_2822`: `arithmetic_error`, `day_of_week_error`, `extraction_error`

## Implication For v0.2

- Carry the format expansion forward.
- Add `unix_epoch` as the first explicitly numeric family.
- Add first-class run versioning and manifests so each phase is publishable on its own.
- Add stricter scoring alongside relaxed semantic correctness so close calls are visible instead of hidden.
- Improve execution throughput before broadening the model matrix.
- Keep the next phase controlled: infrastructure and scoring first, new task families later.
