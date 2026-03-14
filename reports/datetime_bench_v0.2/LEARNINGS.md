# Datetime Benchmark v0.2 Learnings

## Scope

- Formats: `iso_8601`, `rfc_3339`, `rfc_2822`, `natural_language`, `javascript_date`, `python_datetime`, `unix_epoch`
- Cells: 6 (`small/med/large` x `reasoning/non_reasoning`)
- Tasks: 235 scenarios, 7 task families
- Calls: 9,870 total (`1,645` per model cell)
- Token ceiling: `300`
- Run namespace: `runs/datetime_bench_v0.2`
- Total spend: `$26.388947`

## Headline

- `rfc_3339` finished first at `90.99%`
- `python_datetime` finished second at `90.85%`
- `iso_8601` finished third at `90.50%`
- `rfc_3339` was not meaningfully different from `python_datetime` (`p=0.895703`)
- `rfc_3339` was not meaningfully different from `iso_8601` (`p=0.649218`)
- The top tier is now a tight machine-format cluster: `rfc_3339`, `python_datetime`, and `iso_8601`
- `unix_epoch` did not behave like a peer string format; it collapsed to `39.86%`

## What We Learned

- The broader `v0.2` task set did not change the top of the leaderboard. Machine-oriented formats still dominate.
- `rfc_3339` is the best default recommendation now because it finished first, stayed statistically tied with the other top machine forms, and is the most portable strict standard among them.
- `python_datetime` remained exceptionally strong, but it is a runtime-native representation rather than a cross-language interchange target.
- `iso_8601` remained strong, but once `rfc_3339` is measured separately there is less reason to prefer the broader bucket in a system prompt.
- `javascript_date` is workable, but weekday tokens and canonical-shape drift cost real accuracy.
- `natural_language` remained meaningfully worse than the top machine formats, even after reasoning help.
- `rfc_2822` still pays a weekday tax. It is usable, but it is no longer competitive with the top machine-oriented formats.
- `unix_epoch` exposed a different capability regime entirely: the main failure is conversion, not surface formatting.

## What Changed Relative To v0.1.5

- Absolute accuracy dropped across every carry-forward string format because `v0.2` is harder: more tasks, stricter evaluation, and a broader scenario mix.
- The winner changed from `python_datetime` in `v0.1.5` to `rfc_3339` in `v0.2`, but the margin is trivial and not statistically meaningful.
- `rfc_2822` regressed the most among the carry-forward string formats (`-3.83` points), which reinforces the view that weekday-bearing formats are fragile under harder reasoning and extraction tasks.
- `python_datetime`, `rfc_3339`, and `iso_8601` all stayed within about three points of their `v0.1.5` scores despite the harder benchmark, which is a good sign for robustness.
- The new `unix_epoch` family should not be folded into the headline recommendation for formatted timestamps. It is valuable, but it measures numeric datetime conversion more than string-format fluency.

## Strict vs Relaxed Scoring

- `rfc_3339`, `python_datetime`, and `iso_8601` showed no gap between relaxed and strict correctness.
- `javascript_date` dropped from `86.38%` to `80.78%` under strict scoring.
- `natural_language` dropped from `84.33%` to `79.86%` under strict scoring.
- `rfc_2822` dropped from `86.17%` to `82.48%` under strict scoring.
- This is the clearest new signal in `v0.2`: human-readable and runtime-shaped formats often get the right instant while still missing the exact requested surface convention.

## Task-Level Pattern

- `python_datetime` won the hardest arithmetic-heavy families: `multi_hop_reasoning`, `temporal_arithmetic`, `direct_generation`, and `edge_cases`.
- `natural_language` won `extraction_from_passage`, which fits the intuition that prose-heavy contexts help prose-shaped outputs.
- `javascript_date` won `format_conversion`, likely because its verbose token shape makes source-to-target mapping easier once the model has parsed the input.
- `iso_8601` won `multiple_choice_validation`, which suggests models recognize strict canonical machine timestamps very well even when they do not always choose them as the top generative prior.

## Reasoning Effect

- Reasoning improved every format.
- Among string formats, the largest gains were `natural_language` (`+7.52` points), `python_datetime` (`+6.38`), `javascript_date` (`+5.96`), and `rfc_2822` (`+5.53`).
- `rfc_3339` and `iso_8601` also improved, but by less (`+4.11` and `+3.12`).
- `unix_epoch` got the largest raw lift (`+40.00`), but even after that it remained much worse than every string format.

## Error Profile

- `rfc_3339`: mostly `arithmetic_error`, then `extraction_error`
- `python_datetime`: mostly `arithmetic_error`, then `extraction_error`
- `iso_8601`: mostly `arithmetic_error`, then `extraction_error`
- `javascript_date`: `day_of_week_error`, `arithmetic_error`, `extraction_error`
- `natural_language`: `day_of_week_error`, `arithmetic_error`, `timezone_error`
- `rfc_2822`: `day_of_week_error`, `arithmetic_error`, `extraction_error`
- `unix_epoch`: `epoch_conversion_error`, `instruction_violation`, `extraction_error`

## Rescore Note

- After the live run completed, stored outputs were rescored with the patched parser that recognizes `ACST` and `ACDT`.
- `16` rows changed on rescoring.
- The ranking did not change. The only visible aggregate movement was a small `natural_language` increase.

## Implication For v0.3

- Keep `rfc_3339`, `python_datetime`, and `iso_8601` as the top comparison set.
- Keep `unix_epoch`, but report it as a numeric-output family rather than treating it as a direct peer to the string formats.
- Preserve strict scoring. It is surfacing real differences that relaxed semantic correctness hides.
- Expand the benchmark by adding new task families and model coverage, not by replacing the current recommendation logic.
- Default system-prompt recommendation going forward: ask for `RFC 3339` unless there is a concrete runtime-specific reason to prefer Python's native datetime string.
