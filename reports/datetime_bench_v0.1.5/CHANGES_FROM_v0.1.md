# Changes From v0.1 To v0.1.5

## Scope Change

- Expanded from 3 formats to 6 formats:
  - retained: `iso_8601`, `rfc_2822`, `natural_language`
  - added: `rfc_3339`, `javascript_date`, `python_datetime`

## Runtime Change

- Relaxed the token ceiling to `2500`
- Kept the same 6-cell model matrix
- Preserved the original 7 task families

## Why

- The original benchmark answered the standards question, but not the broader “what should I actually ask an LLM to emit?” question.
- Runtime-native formats are common in real systems and deserved direct measurement.
- The relaxed token ceiling removed a known failure mode for reasoning models, especially visible in the earlier GPT-5.4 reasoning behaviour.

## Outcome

- The extension materially changed the headline.
- `python_datetime` and `rfc_3339` joined `iso_8601` as top-tier machine formats.
- `natural_language` and `javascript_date` stayed meaningfully weaker.
