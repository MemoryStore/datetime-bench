# Datetime Benchmark Program Report: v0.3

## Executive summary

The benchmark program still points to the same operational answer:

- use `rfc_3339` by default
- `iso_8601` is effectively tied
- `python_datetime` is fine for Python-only systems
- avoid `javascript_date` and `natural_language` for machine-facing contracts
- treat `unix_epoch` as a separate numeric-conversion task, not a peer formatting recommendation

`v0.3` matters because it tested whether that guidance survives messier inputs. It does.

## What changed from v0.2 to v0.3

`v0.3` kept the benchmark at roughly the same scale, but changed the shape of the work:

- replaced `multiple_choice_validation` with `parsing_normalization`
- added input-style variation
- added timezone-representation variation
- kept `unix_epoch` in the same run but separated it analytically

The recommendation did not materially change. The new evidence mainly sharpened two practical points:

- input normalization matters
- timezone abbreviations are a real source of avoidable failure

## Final v0.3 result

Run stats:

- `22` active cells
- `2` probe-skipped cells
- `36,190` stored result rows
- `$120.64` spend
- `0` stored execution errors

Headline ranking:

| Format | Accuracy | Strict |
| --- | --- | --- |
| `rfc_3339` | 88.24% | 88.24% |
| `iso_8601` | 88.10% | 88.10% |
| `python_datetime` | 87.64% | 87.64% |
| `rfc_2822` | 84.35% | 80.35% |
| `javascript_date` | 78.12% | 73.83% |
| `natural_language` | 76.31% | 71.61% |
| `unix_epoch` | 50.85% | 50.85% |

Program-level conclusion:

- the top recommendation is stable across versions
- the top cluster is now better supported by diverse-input evidence, not just clean prompt templates

## What v0.3 says that v0.2 did not

### 1. The recommendation survives messier inputs

The benchmark no longer depends as heavily on clean canonical prompt shapes.

Aggregate accuracy by input style:

| Input style | Accuracy |
| --- | --- |
| `ambiguous_but_resolved` | 92.76% |
| `compact_structured` | 85.66% |
| `prose_messy` | 78.31% |
| `canonical_text` | 74.99% |

The top string formats still won. That is the main program-level result from `v0.3`.

### 2. Timezone representation is one of the biggest controllable variables

Aggregate accuracy by source timezone style:

| Timezone style | Accuracy |
| --- | --- |
| `utc_or_z` | 85.45% |
| `numeric_offset` | 83.00% |
| `iana_zone` | 76.67% |
| `abbr_or_gmt` | 74.99% |

This is direct implementer guidance:

- prefer `UTC` / `Z` / numeric offsets
- normalize abbreviations before asking for the final emitted timestamp

### 3. Parsing/normalization is strong for top string formats

Best `parsing_normalization` results:

- `iso_8601`: `99.09%`
- `rfc_3339`: strong top-tier behavior
- `python_datetime`: strong top-tier behavior

That means models are not only good at direct formatting. They are also strong at normalizing messy timestamp-like inputs into canonical string forms, as long as the target format is a good one.

### 4. `unix_epoch` improved versus v0.2 but did not become safe

`unix_epoch` moved from `46.60%` in `v0.2` to `50.85%` in `v0.3`.

That is better, but it is not a recommendation change. The gap versus top string formats remains too large to justify using epoch as the default model-emitted representation.

## Format guidance

### Best defaults

`rfc_3339`

- best overall
- portable
- strict contract name
- no weekday tax

`iso_8601`

- effectively tied
- very strong fallback if the existing contract already uses it

`python_datetime`

- excellent in Python-native systems
- not the best cross-language contract

### Formats to avoid as defaults

`javascript_date`

- extra scaffold
- weekday tax
- weaker strict accuracy

`natural_language`

- weakest string format
- phrasing drift
- timezone wording drift
- biggest strict penalty

`unix_epoch`

- numeric conversion problem, not just a formatting problem

## Task-family perspective

Best format by task family:

| Task type | Best format | Best accuracy | Worst format | Worst accuracy |
| --- | --- | --- | --- | --- |
| `multi_hop_reasoning` | `python_datetime` | 86.36% | `unix_epoch` | 45.06% |
| `direct_generation` | `rfc_3339` | 99.87% | `unix_epoch` | 60.26% |
| `temporal_arithmetic` | `rfc_3339` | 79.09% | `unix_epoch` | 40.57% |
| `parsing_normalization` | `iso_8601` | 99.09% | `unix_epoch` | 61.64% |
| `edge_cases` | `python_datetime` | 85.71% | `unix_epoch` | 48.57% |
| `format_conversion` | `iso_8601` | 92.73% | `unix_epoch` | 57.14% |
| `extraction_from_passage` | `rfc_3339` | 79.55% | `unix_epoch` | 46.67% |

Interpretation:

- top string formats remain robust as tasks get harder
- the difficult cases are still arithmetic and multi-hop reasoning
- epoch remains the first thing to break

## Model and reasoning notes

Useful but limited takeaways:

- Google and OpenAI remain strong where implementers care most: top string formats and relatively better epoch handling
- Anthropic is strong on strings and weaker on epoch
- GLM is competitive on strings and weak on epoch
- Qwen trails and also lost one reasoning cell at probe

Reasoning notes:

- reasoning-vs-non-reasoning numbers in this benchmark reflect the actual configured production request shape
- they should not be read as a clean causal estimate of reasoning alone because reasoning cells run at `temperature=1.0` and non-reasoning cells at `0.0`

That caveat matters, but it does not change the practical recommendation about formats.

## Operational observations

The run was slower and more expensive in the tail than the dry run suggested.

What happened:

- the early cheap cells gave a low apparent spend rate
- the expensive large and reasoning cells dominated the final tail
- transient `429` and `503` responses appeared during the run
- retry logic recovered cleanly
- final stored results still had `0` execution errors

Final spend: `$120.64`

That is still safely under the configured soft and hard caps.

## Program conclusion

Across the full benchmark program so far:

- the best production recommendation is stable
- `rfc_3339` is still the best default output contract for LLM-generated timestamps
- `iso_8601` remains a near-tied alternative
- `python_datetime` is excellent but runtime-specific
- `unix_epoch` should not be the default model-emitted representation

`v0.3` did not overturn earlier conclusions. It made them harder to dismiss.
