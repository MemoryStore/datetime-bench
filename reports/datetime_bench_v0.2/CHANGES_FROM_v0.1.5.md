# Changes From v0.1.5 To v0.2

## Goal

Turn the six-format extension into a stable, versioned benchmark baseline that can support broader model coverage and future task expansion without losing comparability.

## Planned Changes

- Add run manifests and versioned artifact paths.
- Reuse cached model selection and dry-run snapshots on resume.
- Raise throughput by improving cell-level and provider-level parallelism.
- Add `strict_correct` alongside relaxed semantic correctness.
- Replace the single blanket tolerance with task-aware semantic thresholds.
- Add `unix_epoch` as a separate numeric-output format family.
- Keep the 6-cell matrix stable for the first `v0.2` run so the scoring and format changes stay attributable.

## What Is Deliberately Deferred

- Input-style diversification
- Parsing-only and validation-only task families
- Prompt paraphrasing
- The full family-balanced matrix

## Why

- `v0.1.5` already showed that the added formats produce distinct behavior.
- The current runner still treats run namespaces as ad hoc.
- Resume is more expensive than it needs to be because dry-run setup is repeated.
- More models are useful only after the benchmark plumbing is stable and the first `v0.2` diff is clean.
