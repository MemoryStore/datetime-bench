# datetime-bench

Benchmark for measuring how reliably LLMs generate datetime values across common output formats.

> [!NOTE]
> _datetime-bench_ was built for [Memory Store](https://memory.store), a cognitive memory architecture for LLM applications. Memory Store uses LLMs to resolve relative time expressions into grounded timestamps for episodic memory, so datetime format choice is a production concern.

## tl;dr

> [!TIP]
> If you ask an LLM to emit a machine-facing timestamp, use `rfc_3339`.

- Default: `rfc_3339`
- Also good: `iso_8601`
- Fine for Python-only systems: `python_datetime`
- Avoid for machine-facing contracts: `javascript_date`, `natural_language`
- Do not ask the model for `unix_epoch` unless you have to; emit a string timestamp and convert to epoch in code

`v0.3` confirms the same practical story as earlier versions, but under a more realistic benchmark shape: input diversity and parsing/normalization did not change the top recommendation. The best string formats are still a tight cluster, and `unix_epoch` is still far worse than every string format.

## Why this benchmark exists

LLM applications routinely turn relative or natural-language datetime mentions into grounded timestamps: "last Tuesday", "three hours ago", "the meeting after lunch". The output format matters because downstream code has to parse it reliably. A format that models generate incorrectly 10% of the time means 10% of timestamps are silently wrong before your application even starts validating business logic.

This benchmark measures first-attempt generation reliability. It is aimed at implementers deciding what timestamp format to request from a model in production.

## v0.3 headline results

`v0.3` is the current benchmark baseline.

- `22` active model cells across Google, Anthropic, OpenAI, Qwen, and GLM
- `2` probe-skipped cells: `qwen_large_r`, `glm_med_r`
- `235` scenarios
- `7` output formats
- `36,190` stored result rows
- `$120.64` total spend

| Format | Accuracy | Strict | 95% CI |
| --- | --- | --- | --- |
| `rfc_3339` | 88.24% | 88.24% | 87.33-89.09% |
| `iso_8601` | 88.10% | 88.10% | 87.19-88.96% |
| `python_datetime` | 87.64% | 87.64% | 86.72-88.51% |
| `rfc_2822` | 84.35% | 80.35% | 83.34-85.32% |
| `javascript_date` | 78.12% | 73.83% | 76.98-79.23% |
| `natural_language` | 76.31% | 71.61% | 75.13-77.44% |
| `unix_epoch` | 50.85% | 50.85% | 49.49-52.21% |

Recommendation:

- Use `rfc_3339` by default
- Treat `iso_8601` as effectively tied, but less precise as a prompt contract
- Use `python_datetime` only when the consumer is explicitly Python-native
- Treat `unix_epoch` as a separate numeric-conversion problem, not a peer string format

## What to use and what to avoid

### Use this by default

`rfc_3339`

Why:
- best overall string-format accuracy in `v0.3`
- statistically tied with `iso_8601` and `python_datetime`
- strict, portable, and cross-language
- no weekday token, so no strict-vs-relaxed penalty

### Also acceptable

`iso_8601`

Why:
- effectively tied with `rfc_3339`
- strong syntactic validity and strong semantic accuracy

Tradeoff:
- broader name than the actual wire shape you usually want

### Use only when your stack is Python-specific

`python_datetime`

Why:
- nearly tied with the top two
- excellent for Python-native systems

Tradeoff:
- runtime-specific string shape, weaker as a cross-language API contract

### Avoid for machine-facing output

`javascript_date`

Why:
- weekday tax
- extra scaffold tokens
- lower strict accuracy

`natural_language`

Why:
- weakest string format
- phrasing drift and timezone wording drift
- highest strict penalty among string formats

### Treat separately

`unix_epoch`

Why:
- only `50.85%` overall
- much worse on arithmetic-heavy tasks
- best practice is to have the model emit a canonical string timestamp and convert to epoch in deterministic code

## What LLMs are good at

- emitting canonical string timestamps
- parsing and normalizing compact structured inputs
- handling `UTC`, `Z`, and numeric offsets
- direct generation in top string formats

## What LLMs are bad at

- exact epoch conversion
- arithmetic-heavy datetime tasks
- multi-hop temporal reasoning
- timezone abbreviations and `GMT`-style wording
- weekday-bearing formats

## Input-side findings that matter in production

Timezone representation matters.

Aggregate accuracy by source timezone style:

| Source timezone style | Accuracy |
| --- | --- |
| `utc_or_z` | 85.45% |
| `numeric_offset` | 83.00% |
| `iana_zone` | 76.67% |
| `abbr_or_gmt` | 74.99% |

Practical advice:

- Prefer `UTC`, `Z`, or explicit numeric offsets in prompts and intermediate representations
- Prefer normalizing timezone abbreviations before asking the model for a final machine-facing timestamp
- Do not assume that familiar abbreviations like `EST`, `PDT`, or `GMT+0000` are safer than explicit offsets; they were worse

For the top formats, the ugliest source pattern in `v0.3` was canonical text paired with timezone abbreviations:

| Format | Canonical text + `abbr_or_gmt` |
| --- | --- |
| `rfc_3339` | 59.60% |
| `iso_8601` | 60.10% |
| `python_datetime` | 55.56% |

That is the strongest practical reason to normalize timezone wording before the final formatting step.

## Task-level findings

Best format by task family:

| Task type | Best format | Accuracy | Worst format | Accuracy |
| --- | --- | --- | --- | --- |
| `direct_generation` | `rfc_3339` | 99.87% | `unix_epoch` | 60.26% |
| `temporal_arithmetic` | `rfc_3339` | 79.09% | `unix_epoch` | 40.57% |
| `multi_hop_reasoning` | `python_datetime` | 86.36% | `unix_epoch` | 45.06% |
| `format_conversion` | `iso_8601` | 92.73% | `unix_epoch` | 57.14% |
| `extraction_from_passage` | `rfc_3339` | 79.55% | `unix_epoch` | 46.67% |
| `edge_cases` | `python_datetime` | 85.71% | `unix_epoch` | 48.57% |
| `parsing_normalization` | `iso_8601` | 99.09% | `unix_epoch` | 61.64% |

Takeaway:

- top string formats stay strong across all task families
- temporal arithmetic and multi-hop reasoning remain the weak spots
- `unix_epoch` collapses hardest exactly where you would least want hidden errors

## Model-family takeaways

Short version:

- Google and OpenAI are strong on string formats and comparatively strong on epoch
- Anthropic is solid on strings, weaker on epoch
- GLM is competitive on strings and weak on epoch
- Qwen trails materially
- two reasoning cells failed probe and were skipped: `qwen_large_r`, `glm_med_r`

This benchmark is primarily about format choice, not a model leaderboard, but the model-family pattern is stable enough to matter if you depend on epoch or arithmetic-heavy timestamp generation.

## Why `rfc_3339` still wins

`rfc_3339` and `iso_8601` are effectively tied in this benchmark because the requested output shape is the same full timestamp shape. The reason to prefer `rfc_3339` anyway is contract clarity.

If you ask for `rfc_3339`, you are asking for a narrow, specific timestamp shape.

If you ask for `iso_8601`, you are asking for a broader family of valid shapes.

The benchmark result says:
- both are good
- `rfc_3339` is the better production prompt contract

## Artifacts

Current v0.3 report artifacts:

- [summary.md](reports/datetime_bench_v0.3/summary.md)
- [LEARNINGS.md](reports/datetime_bench_v0.3/LEARNINGS.md)
- [PROGRAM_REPORT.md](reports/datetime_bench_v0.3/PROGRAM_REPORT.md)
- [format_comparison_string_only.csv](reports/datetime_bench_v0.3/format_comparison_string_only.csv)
- [epoch_summary.csv](reports/datetime_bench_v0.3/epoch_summary.csv)
- [input_variant_summary.csv](reports/datetime_bench_v0.3/input_variant_summary.csv)
- [cost_report.csv](reports/datetime_bench_v0.3/cost_report.csv)

> [!IMPORTANT]
> The checked-in `reports/` directory is a publication snapshot. The run artifacts and generated CSVs for `v0.3` are included in this checkout, but earlier historical runs are not all present in raw form.

> [!IMPORTANT]
> Benchmark request shape is intentional: reasoning cells run at `temperature=1.0`, non-reasoning cells at `temperature=0.0`. Read reasoning-vs-non-reasoning comparisons as production-configuration comparisons, not a clean causal estimate of "reasoning effect".

## Version history

| Version | Main result | Spend |
| --- | --- | --- |
| `v0.1` | `iso_8601` led the original three-format benchmark | ~$7.45 |
| `v0.1.5` | `python_datetime`, `rfc_3339`, and `iso_8601` formed a top cluster | ~$15.37 |
| `v0.2` | same practical recommendation, with stronger family/size evidence | $148.45 |
| `v0.3` | same recommendation holds under input diversity and parsing/normalization | $120.64 |

The recommendation did not materially change across versions. `v0.3` mostly strengthens confidence that the advice survives messier and more realistic inputs.

## Running the benchmark

```bash
uv sync
export OPENROUTER_API_KEY="sk-or-..."

# Dry run
datetime-bench --dry-run

# Full run
datetime-bench
```

Raw artifacts go to `runs/`. Analysis outputs go to `reports/`.

## Repo layout

```text
src/datetime_bench/
  config.py
  runner.py
  openrouter.py
  analysis.py
  evaluation/
  tasks/
reports/
  datetime_bench_v0.1/
  datetime_bench_v0.1.5/
  datetime_bench_v0.2/
  datetime_bench_v0.3/
```
