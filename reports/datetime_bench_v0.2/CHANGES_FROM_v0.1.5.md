# Changes From v0.1.5 To v0.2

## Scope Change

- Expanded from 6 formats to 7: added `unix_epoch`
- Expanded from 6 confounded model cells to 24 family-controlled cells:
  - Google: flash-lite / flash / pro × nr/r
  - Anthropic: haiku / sonnet / opus × nr/r
  - OpenAI: gpt-5-mini / gpt-5.1 / gpt-5.3-chat / gpt-5.4 × nr/r
  - Open-source: qwen3.5-9b, qwen3.5-27b, glm-5 × nr/r
- Increased n per task type from 20 to 35–45
- Edge cases now randomizable beyond the core 20

## Infrastructure Changes

- Run manifests and versioned artifact paths (`layout.py`)
- Cached model selection and dry-run snapshots on resume (`--refresh-setup` to override)
- Cell-parallel execution (12 concurrent, per-provider rate limiters)
- `strict_correct` tracked alongside relaxed semantic correctness
- Task-aware semantic thresholds (0s default, 60s for multi_hop/extraction)
- MAX_COMPLETION_TOKENS raised from 150 to 2500
- Reasoning cells use temperature 1.0; non-reasoning cells use 0.0
- Non-reasoning cells no longer send `{"enabled": false}` reasoning config (avoids "reasoning is mandatory" errors)

## What Was Deliberately Deferred

- Input-style diversification (v0.3)
- Parsing-only and validation-only task families (v0.3)
- Prompt paraphrasing (v0.4.1)
- Temporal reasoning expansion (v0.4)

## Why

- v0.1.5 showed the format ranking is real but the model matrix was confounded — couldn't attribute effects to size vs family
- unix_epoch tests a fundamentally different skill (numeric↔calendar conversion)
- Stricter scoring surfaces real differences hidden by the blanket ±60s threshold
- More models are only useful with proper infrastructure (parallelism, resume, versioning)

## Outcome

- 24/25 cells completed successfully (qwen3.5-9b reasoning failed probe)
- 39,480 total calls, $148.45 total spend
- Format ranking held across all families — now confirmed as a format property, not a model quirk
- unix_epoch at 46.60% confirmed as a distinct capability regime
- Weekday tax quantified at ~5–6 pts via strict scoring
