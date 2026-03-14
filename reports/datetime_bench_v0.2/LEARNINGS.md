# Datetime Benchmark v0.2 Learnings

## Scope

- Formats: `iso_8601`, `rfc_3339`, `rfc_2822`, `natural_language`, `javascript_date`, `python_datetime`, `unix_epoch` (new)
- Cells: 24 active + 1 skipped (`qwen_small_r` — Qwen 3.5 9B reasoning failed probe)
  - Google: flash-lite, flash, pro × nr/r (6)
  - Anthropic: haiku, sonnet, opus × nr/r (6)
  - OpenAI: gpt-5-mini, gpt-5.1, gpt-5.3-chat, gpt-5.4 × nr/r (7)
  - Open-source: qwen3.5-9b nr, qwen3.5-27b × nr/r, glm-5 × nr/r (5)
- Tasks: 235 scenarios, 7 task families, 1645 cases per model
- Token ceiling: 2500
- Semantic thresholds: 0s default, 60s for multi_hop and extraction
- Strict correctness tracked alongside relaxed
- Total spend: $148.45
- Total calls: 39,480

## Headline

| Format | Accuracy | Strict | 95% CI |
|--------|----------|--------|--------|
| iso_8601 | 86.83% | 86.83% | 85.9–87.7% |
| python_datetime | 86.52% | 86.52% | 85.6–87.4% |
| rfc_3339 | 86.40% | 86.40% | 85.5–87.3% |
| rfc_2822 | 82.50% | 76.95% | 81.5–83.5% |
| javascript_date | 79.79% | 73.87% | 78.7–80.8% |
| natural_language | 79.29% | 72.78% | 78.2–80.3% |
| unix_epoch | 46.60% | 46.60% | 45.3–47.9% |

- Top tier: `iso_8601` ≈ `python_datetime` ≈ `rfc_3339` (all p > 0.5 pairwise)
- Middle tier: `rfc_2822` > `javascript_date` ≈ `natural_language`
- `unix_epoch` is a different regime entirely

## What We Learned

### 1. The format ranking is robust across model families

The top-3 / middle-3 ordering held across all five provider families (Google, Anthropic, OpenAI, Qwen, GLM). No family produced a different format ranking. This is the strongest evidence yet that the ranking reflects format properties, not model quirks.

### 2. unix_epoch exposes a deep capability gap

- Overall: 46.60% — dramatically below every string format
- `direct_generation` epoch (the simplest task): only 52.38%, vs 97%+ for string formats
- Family spread is enormous: Google 65.96%, OpenAI 61.70%, Anthropic 32.98%, Qwen 23.83%, GLM 10.64%
- Reasoning is transformative for epoch: many cells jump from near-0% (nr) to 60–100% (r)
- Qwen 9B and Qwen 27B (nr) scored 0% on epoch across all task types — they cannot do numeric-to-calendar conversion without reasoning
- Epoch should be reported as a separate numeric-conversion family, not aggregated with string formats

### 3. Strict vs relaxed reveals the weekday tax

Formats without weekday tokens show no strict/relaxed gap:
- iso_8601: 86.83% / 86.83% (Δ 0.00)
- python_datetime: 86.52% / 86.52% (Δ 0.00)
- rfc_3339: 86.40% / 86.40% (Δ 0.00)

Weekday formats show a consistent ~5–6 pt drop:
- rfc_2822: 82.50% → 76.95% (Δ −5.55)
- javascript_date: 79.79% → 73.87% (Δ −5.92)
- natural_language: 79.29% → 72.78% (Δ −6.51)

The gap is entirely day-of-week computation errors — models get the datetime right but the weekday wrong.

### 4. Family comparison

| Family | iso_8601 | Best Non-Epoch | Epoch | N |
|--------|----------|----------------|-------|---|
| Google | 90.64% | python 91.13% | 65.96% | 1410 |
| OpenAI | 89.18% | iso 89.18% | 61.70% | 1645 |
| Anthropic | 87.16% | iso/python/rfc3339 ~87.1% | 32.98% | 1410 |
| GLM | 90.43% | iso 90.43% | 10.64% | 470 |
| Qwen | 70.64% | python 71.35% | 23.83% | 705 |

- **Google leads on string formats and dominates epoch** — Pro and Flash are strong across the board
- **GLM-5 is surprisingly competitive on string formats** (90.43% iso) but catastrophic on epoch (10.64%)
- **Anthropic is solid but epoch-weak** — extended thinking helps but not enough
- **OpenAI is strong and epoch-capable** — gpt-5.3-chat scored 100% on direct_generation epoch
- **Qwen trails significantly** — 9B is especially weak, 27B better but well below frontier

### 5. Size effect within families

Anthropic (cleanest comparison — same architecture, 3 sizes, both reasoning modes):
- Haiku (small): ~72% avg across string formats
- Sonnet (medium): ~85%
- Opus (large): ~88%
- Scaling: +13 pts small→med, +3.4 pts med→large (diminishing returns at the top)

Google (3 sizes, both reasoning modes):
- Flash-Lite (small): ~84%
- Flash (medium): ~88%
- Pro (large): ~92%
- Consistent +4 pts per tier

### 6. Reasoning effect

- For string formats: reasoning generally helps but the effect is model- and format-dependent
- For epoch: reasoning is transformative — many cells go from near-0% to 60–100%
- Qwen 9B reasoning failed the probe entirely — reasoning mode isn't functional for datetime tasks
- The biggest reasoning lifts are on formats that require computation (epoch, weekday-bearing formats)

### 7. format_conversion → natural_language remains the hardest non-epoch cell

- 65.24% average — the only non-epoch cell below 70%
- OpenAI reasoning models particularly weak (gpt-5.4 reasoning: 37.14%)
- Converting to NL requires both format translation and weekday/AM-PM/timezone-name generation

### 8. Cost distribution

- Total: $148.45 across 39,480 calls ($0.00376/call avg)
- Most expensive: google_large_nr ($23.01), qwen_large_r ($22.66), google_large_r ($15.79)
- Cheapest: qwen_small_nr ($0.04), google_small_nr ($0.13)
- 350× cost ratio (cheapest to most expensive cell) for ~20 pt accuracy difference

## What Changed Relative To v0.1.5

- Model matrix: 6 confounded cells → 24 family-controlled cells
- Added unix_epoch (7th format) — exposed major capability gap
- Added tiered semantic thresholds (0s default, 60s for multi_hop/extraction)
- Added strict_correct tracking — quantified weekday tax at ~5–6 pts
- Increased n per type (35–45, up from 20)
- Edge cases now randomizable beyond core 20
- MAX_COMPLETION_TOKENS: 150 → 2500
- Parallel cell execution (12 concurrent)

## Implications For v0.3

- Format ranking is settled. v0.3 should test whether it holds under diverse input representations.
- unix_epoch needs its own analysis section — aggregating it with string formats distorts headlines.
- Strict/relaxed gap on weekday formats should be a first-class metric.
- Qwen 9B reasoning should be dropped from future runs (genuine capability limit).
- GLM-5's strong string-format / weak epoch pattern is worth investigating.
- System-prompt recommendation: use `rfc_3339` or `python_datetime` for machine contexts, `iso_8601` as a safe default. Avoid `natural_language` and `unix_epoch` unless the consuming system requires them.
