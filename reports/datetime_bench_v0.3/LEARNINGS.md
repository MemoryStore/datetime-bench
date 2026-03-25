# Datetime Benchmark v0.3 Learnings

## Headline

`v0.3` did not change the practical recommendation.

- Default machine-facing format: `rfc_3339`
- Also good: `iso_8601`
- Python-only internal systems: `python_datetime`
- Avoid for machine-facing output: `javascript_date`, `natural_language`
- Do not ask the model for `unix_epoch` unless the consuming system forces it

`v0.3` added input diversity and a parsing/normalization family. The recommendation survived.

## Run shape

- `22` active cells
- `2` probe-skipped cells: `qwen_large_r`, `glm_med_r`
- `235` scenarios
- `36,190` stored result rows
- `$120.64` spend
- `0` stored execution errors

## Final ranking

| Format | Accuracy | Strict |
| --- | --- | --- |
| `rfc_3339` | 88.24% | 88.24% |
| `iso_8601` | 88.10% | 88.10% |
| `python_datetime` | 87.64% | 87.64% |
| `rfc_2822` | 84.35% | 80.35% |
| `javascript_date` | 78.12% | 73.83% |
| `natural_language` | 76.31% | 71.61% |
| `unix_epoch` | 50.85% | 50.85% |

## What we learned

### 1. The top recommendation is stable

The top cluster is still:

- `rfc_3339`
- `iso_8601`
- `python_datetime`

The differences at the top are small. The reason to pick `rfc_3339` is not just that it finished first. It is that it finished first while also being the cleanest cross-language contract.

### 2. `unix_epoch` is still a separate problem class

Overall epoch accuracy was `50.85%`.

Hard-task epoch accuracy:

- `temporal_arithmetic`: `40.57%`
- `multi_hop_reasoning`: `45.06%`
- `extraction_from_passage`: `46.67%`

Better epoch cases:

- `parsing_normalization`: `61.64%`
- `direct_generation`: `60.26%`

Interpretation:

- models are much better at canonical string timestamps than exact numeric timestamp conversion
- if you need epoch, generate a strong string format first and convert deterministically in code

### 3. Input representation matters more than the top-line table suggests

Aggregate accuracy by source timezone style:

| Source style | Accuracy |
| --- | --- |
| `utc_or_z` | 85.45% |
| `numeric_offset` | 83.00% |
| `iana_zone` | 76.67% |
| `abbr_or_gmt` | 74.99% |

This is one of the most actionable findings in the run.

Practical implication:

- prefer `UTC`, `Z`, or explicit offsets whenever you can
- normalize abbreviations like `EST`, `PDT`, and `GMT+0000` before asking for the final output

For the top formats, canonical text with timezone abbreviations was especially bad:

- `rfc_3339`: `59.60%`
- `iso_8601`: `60.10%`
- `python_datetime`: `55.56%`

### 4. Compact structured inputs are safer than free-form prose

Aggregate accuracy by input style:

| Input style | Accuracy |
| --- | --- |
| `ambiguous_but_resolved` | 92.76% |
| `compact_structured` | 85.66% |
| `prose_messy` | 78.31% |
| `canonical_text` | 74.99% |

Practical implication:

- if your pipeline can normalize source text before the final formatting prompt, do it
- compact structured intermediate forms are a safer handoff format than natural-language restatements

### 5. Weekday-bearing formats still pay a real tax

Strict penalties:

- `rfc_2822`: `84.35% -> 80.35%`
- `javascript_date`: `78.12% -> 73.83%`
- `natural_language`: `76.31% -> 71.61%`

The model often gets the instant right but the weekday token wrong. That is why machine-facing formats without weekday tokens remain the safer contract.

### 6. Top string formats hold up across task families

Best format by task family:

| Task type | Best format | Accuracy |
| --- | --- | --- |
| `direct_generation` | `rfc_3339` | 99.87% |
| `temporal_arithmetic` | `rfc_3339` | 79.09% |
| `multi_hop_reasoning` | `python_datetime` | 86.36% |
| `format_conversion` | `iso_8601` | 92.73% |
| `extraction_from_passage` | `rfc_3339` | 79.55% |
| `edge_cases` | `python_datetime` | 85.71% |
| `parsing_normalization` | `iso_8601` | 99.09% |

Practical implication:

- `rfc_3339`, `iso_8601`, and `python_datetime` are robust choices even when the task changes
- the benchmark is not just measuring one easy transcription pattern

### 7. Model-family differences matter most on epoch

The family pattern is useful, but only to a point.

- frontier families are all strong enough on string formats that format choice matters more than family choice
- epoch is where family differences become large
- skipped probe cells matter: `qwen_large_r` and `glm_med_r` were not omitted for convenience; they failed probe compatibility

Practical implication:

- if your workload depends on epoch or heavy temporal arithmetic, do not assume string-format strength transfers automatically

### 8. The run was operationally stable

- transient `429` and `503` responses happened during execution
- retries recovered them
- final stored result rows had `0` execution errors

This matters because the benchmark output is usable as a clean publication snapshot rather than a partially degraded run.

## What to do in production

If you need a timestamp from an LLM:

1. Ask for `rfc_3339`
2. Prefer prompts or intermediate inputs that use `UTC`, `Z`, or explicit numeric offsets
3. Normalize timezone abbreviations before the final formatting request
4. Avoid weekday-bearing output formats unless the downstream contract explicitly requires them
5. If you need epoch, convert from a canonical string in code instead of asking the model for the integer directly
