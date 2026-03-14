# Datetime Benchmark Program Report

This report summarizes the datetime-format benchmark program through `v0.2`. It ties together the earlier three-format runs, the format expansion, the few-shot extension, and the current `v0.2` baseline.

## Executive Summary

The program started with one question: what timestamp format do current LLMs generate most reliably when asked to emit only a datetime string? The answer changed less than expected as the benchmark expanded.

The earliest three-format work already showed a clear pattern: machine-oriented formats beat wordier human-readable ones. That result held through every follow-on run. What changed over time was the recommendation.

- In the original three-format comparison, `ISO 8601` was the strongest default.
- After adding `RFC 3339` and Python and JavaScript runtime-native string forms, the top of the leaderboard became a tight machine-format cluster.
- In `v0.2`, `RFC 3339` finished first at `90.99%`, but it was statistically tied with `python_datetime` (`90.85%`) and `iso_8601` (`90.50%`).
- `RFC 3339` is now the default recommendation because it is strict, portable, and cross-language, while keeping essentially all of the reliability of the strongest alternatives.

The clearest negative result is also stable: `unix_epoch` does not behave like a peer string format. It is a separate numeric-conversion task family, and performance collapsed to `39.86%` in `v0.2`.

## Run History

| Phase | Format set | Main finding | Spend |
| --- | --- | --- | --- |
| Early pilot | `iso_8601`, `rfc_2822`, `natural_language` | `iso_8601` led; the broad conclusion was already visible | `$4.659077` |
| `v0.1` baseline | same 3 formats | `iso_8601` stayed on top at `92.74%` | `$7.454499` |
| Few-shot extension | `natural_language` only | three exemplars lifted `natural_language` from `86.67%` to `91.55%` | `$2.947685` |
| `v0.1.5` | 6 formats | `python_datetime` moved to the top at `93.81%`; `rfc_3339` stayed close at `93.21%` | `$15.366276` |
| `v0.2` | 7 formats, expanded tasks, strict scoring | `rfc_3339` moved into first place at `90.99%`, but remained statistically tied with `python_datetime` and `iso_8601` | `$26.388947` |

The early pilot is not preserved as a versioned artifact because it was superseded by the committed three-format baseline. It still matters because it showed that the headline ranking was not an artifact of one token budget or one reasoning configuration.

## Phase-by-Phase Findings

### 1. Three-format baseline: `ISO 8601` won the original question

The first benchmark asked the cleanest question: among `ISO 8601`, `RFC 2822`, and structured natural language, which one is most reliable for first-attempt generation?

The answer was `ISO 8601`.

- Early pilot: `iso_8601 92.74%`, `natural_language 87.98%`, `rfc_2822 87.98%`
- `v0.1` baseline: `iso_8601 92.74%`, `rfc_2822 88.57%`, `natural_language 86.67%`

That ranking was stable across size buckets. The interesting nuance was reasoning: it barely moved `ISO 8601`, but it helped `RFC 2822` enough to narrow the gap. That told us the main weakness in `RFC 2822` was not token familiarity alone. It was the extra work imposed by day names and offset formatting.

### 2. Relaxed-token rerun: the headline survived more permissive output budgets

The relaxed rerun increased `max_tokens` to `2500` to remove visible-output starvation for larger reasoning models. That let `openai/gpt-5.4` and `google/gemini-3.1-pro-preview` participate cleanly in the three-format sweep.

The ranking did not change.

- `iso_8601 92.74%`
- `rfc_2822 88.57%`
- `natural_language 86.67%`

This mattered because it ruled out a simple explanation: the original result was not just a byproduct of tight completion budgets. The drawback is that the rerun also showed a real operational issue with larger reasoning models: they remain much more fragile under tight visible-token limits, even when the final answer is short.

### 3. Few-shot extension: examples helped prose-shaped output, but did not overturn the baseline

The first extension targeted the weakest format from the relaxed three-format run: structured natural language. Adding three task-matched exemplars improved `natural_language` from `86.67%` to `91.55%`, a `+4.88` point lift.

That result was useful for two reasons.

First, it showed that some of the natural-language deficit was promptable rather than inherent. Second, it set a ceiling on what few-shot prompt engineering was likely to buy us. Even after the lift, `natural_language` still trailed zero-shot `iso_8601` in the same benchmark family.

The gains were not uniform. The biggest improvements came in smaller and mid-tier reasoning cells. Large reasoning models did not improve in the same way, which suggests that few-shot examples helped weaker or more brittle decoders anchor the output shape more than they helped the strongest models.

### 4. `v0.1.5`: six formats produced a top-tier machine-format cluster

The six-format expansion added `rfc_3339`, `python_datetime`, and `javascript_date` to the original three formats. This was the first run where the original question changed shape: it stopped being about one standards-track format versus another, and became a broader comparison between machine-oriented, runtime-native, and human-readable timestamp forms.

Headline result:

- `python_datetime 93.81%`
- `rfc_3339 93.21%`
- `iso_8601 92.86%`
- `rfc_2822 90.00%`
- `javascript_date 88.81%`
- `natural_language 86.43%`

This was the first time `ISO 8601` was no longer the top row. The more important finding, though, was not that Python's native string happened to edge it out. It was that the leaderboard now had a clear top tier made of machine-oriented shapes:

- `python_datetime`
- `rfc_3339`
- `iso_8601`

All three were better than the wordier alternatives, and `python_datetime` and `rfc_3339` were statistically tied. That is the point where the recommendation started to shift from “use ISO 8601” to “use a strict machine format, and prefer the most portable one.”

`javascript_date` was informative. It was usable, but it paid a real weekday tax. The format carries more natural-language tokens than the top machine forms, but that did not translate into higher reliability. It mostly created more ways to be almost right without being exactly right.

### 5. `v0.2`: stricter scoring, broader tasks, and `unix_epoch`

`v0.2` is the current baseline. It is the first run that should be treated as the stable benchmark rather than an exploration pass.

What changed:

- format set grew to seven with `unix_epoch`
- task count grew from `140` to `235`
- total calls grew to `9,870`
- `strict_correct` was added alongside relaxed semantic correctness
- task-aware thresholds replaced a single blanket tolerance
- reports and manifests became versioned

Headline result:

- `rfc_3339 90.99%`
- `python_datetime 90.85%`
- `iso_8601 90.50%`
- `javascript_date 86.38%`
- `rfc_2822 86.17%`
- `natural_language 84.33%`
- `unix_epoch 39.86%`

The absolute scores dropped because `v0.2` is harder. That is expected. The important thing is what did not change:

- the top of the table still belongs to machine-oriented formats
- `rfc_3339`, `python_datetime`, and `iso_8601` are still clustered tightly together
- `rfc_3339` is statistically tied with both of the next two formats

This is why `RFC 3339` is now the default recommendation. It gives the benchmark’s best headline score, but more importantly it does so without requiring a runtime-specific representation like Python’s `str(datetime)`.

## What the benchmark says about each format

### `RFC 3339`

This is the best default target now.

It stayed in the top cluster in the six-format run and moved into first place in `v0.2`. It also showed no gap between relaxed and strict correctness in `v0.2`, which matters. The model is not just producing the right instant; it is producing the requested shape.

The main remaining failures are arithmetic and extraction mistakes, not surface-form confusion. That is the kind of error profile you want in a system-prompt default.

### `python_datetime`

Python’s native aware datetime string is the other serious contender.

It won `v0.1.5` and remained statistically tied for first in `v0.2`. It also won the hardest arithmetic-heavy `v0.2` task families: `multi_hop_reasoning`, `temporal_arithmetic`, `direct_generation`, and `edge_cases`.

The reason it is not the default recommendation is not quality. It is portability. If the caller is Python-specific, this is an excellent target. If the caller is building a general LLM contract or cross-language interface, `RFC 3339` is the safer standard to optimize for.

### `ISO 8601`

`ISO 8601` remained strong across every phase. It won the original benchmark question and never fell out of the top tier.

What changed is that once `RFC 3339` is measured separately, there is less reason to ask for the broader `ISO 8601` bucket in prompts. `RFC 3339` captures the portable machine-format benefits while removing some ambiguity about the exact surface shape.

### `RFC 2822`

The original hypothesis was that `RFC 2822` might outperform `ISO 8601` because weekday and month names are familiar natural-language tokens. The data does not support that.

`RFC 2822` is usable, and reasoning helps it more than it helps the best machine forms, but it consistently pays a weekday tax. In `v0.2`, its main errors were still `day_of_week_error`, `arithmetic_error`, and `extraction_error`.

The problem is structural: `RFC 2822` carries more surface obligations than the top machine forms, and those obligations create more ways to fail.

### Structured natural language

Structured natural language is readable and flexible, but that flexibility cuts both ways.

It improved substantially under few-shot prompting and it won `extraction_from_passage` in `v0.2`, which makes sense in prose-heavy contexts. But it consistently trailed the top machine formats. The strict-vs-relaxed gap in `v0.2` also shows that natural-language answers often represent the right instant while still drifting away from the requested convention.

That makes it a weaker default contract format, even if it remains useful in user-facing prose.

### JavaScript full date strings

JavaScript-style full date strings are workable, but not attractive as a default.

They lost ground to the top machine formats in both six-format and `v0.2` runs. The format conversion task liked them, probably because the token-rich shape makes source-target mapping easier once the model has already parsed the input. But strict scoring exposed the downside: weekday tokens and natural-language scaffolding create more room for “almost right” answers.

### `unix_epoch`

This is the important negative control.

`unix_epoch` did not merely underperform. It behaved like a different problem class. In `v0.2`, the dominant error was `epoch_conversion_error`, followed by instruction violations and extraction mistakes. Reasoning helped a lot in absolute terms, but the format still finished far behind every string format.

That does not mean epoch output is useless. It means it should be benchmarked and interpreted separately. Asking a model for an integer timestamp is much closer to asking it to do an exact numeric conversion than to asking it to emit a canonical string.

## Strict vs relaxed scoring changed what we could see

`v0.2` introduced the most important measurement improvement in the whole program: `strict_correct`.

For the top machine formats, strict and relaxed correctness were identical:

- `rfc_3339`: `90.99%` strict and relaxed
- `python_datetime`: `90.85%` strict and relaxed
- `iso_8601`: `90.50%` strict and relaxed

That is strong evidence that these formats are not just semantically correct. They are the shapes models actually want to emit once they have the right answer.

The weaker formats showed meaningful drops:

- `javascript_date`: `86.38%` to `80.78%`
- `natural_language`: `84.33%` to `79.86%`
- `rfc_2822`: `86.17%` to `82.48%`

This is the cleanest argument against relying on the looser human-readable formats for system contracts. They are much more likely to be semantically right while still failing the requested surface convention.

## Task sensitivity and error patterns

The benchmark now has enough surface area to say something more specific than “some formats are better than others.”

### The hardest task families favor machine-native shapes

In `v0.2`, the widest task spreads were:

- `multi_hop_reasoning`: `python_datetime 93.81%` vs `unix_epoch 21.90%`
- `temporal_arithmetic`: `python_datetime 87.50%` vs `unix_epoch 24.58%`
- `direct_generation`: `python_datetime 100.00%` vs `unix_epoch 44.29%`

Among string formats only, the same basic story holds: the top machine formats are robust under arithmetic and chained reasoning, while the human-readable formats lose ground as the task becomes less about transcription and more about exact temporal state updates.

### The error profile is stable enough to trust

Across phases, the same patterns recur.

- Machine formats: mostly arithmetic and extraction mistakes
- `RFC 2822` and JS/NL full-date strings: weekday and convention drift
- Natural language: timezone and day-of-week errors on top of arithmetic issues
- `unix_epoch`: exact numeric conversion failures

Those are not noisy one-off results. They line up with the qualitative shape of each format.

## Current recommendation

For “instruct an LLM in a system prompt to generate timestamps in X format,” the current recommendation is:

1. Use `RFC 3339` by default.
2. Use `python_datetime` only when the consuming system is explicitly Python-native and that exact representation is what downstream code expects.
3. Keep `ISO 8601` as an acceptable alternative, but prefer `RFC 3339` when you want a strict portable contract.
4. Do not use `RFC 2822`, natural language, or JavaScript full date strings as the default machine-facing output contract.
5. Treat `unix_epoch` as a separate numeric-output task family, not as a peer string-format choice.

## What changed in `v0.2`, and what should come next

`v0.2` did two things well.

It widened the benchmark enough to make the current recommendation harder to dismiss as a quirk of one task set. And it introduced strict scoring, which made the difference between “the model knew the answer” and “the model produced the requested representation” visible.

The next phase should build on that, not restart the question.

The high-value next steps are:

- keep `rfc_3339`, `python_datetime`, and `iso_8601` as the core top-tier comparison set
- keep `unix_epoch`, but report it separately as a numeric-output family
- expand task families and model coverage without changing the scoring contract again
- preserve versioned artifacts and narrative deltas so each run remains interpretable on its own

The main open question is no longer which broad family of format wins. That part is answered. The next useful question is how stable the `rfc_3339` recommendation remains as the model matrix widens and the task set becomes more varied.
