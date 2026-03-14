# Datetime Format Benchmark Summary

## Model Selection
| Cell                | Selected Model                       | Mode          | Notes                                                                                                                                                                                                                                                                                                                                                                          |
| ------------------- | ------------------------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| small_non_reasoning | google/gemini-3.1-flash-lite-preview | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3.1-flash-lite-preview                                                                                                                                                                           |
| med_non_reasoning   | anthropic/claude-sonnet-4.6          | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                                                                                                                                                                                                        |
| large_non_reasoning | anthropic/claude-opus-4.6            | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                                                                                                                                                                                                        |
| small_reasoning     | google/gemini-3-flash-preview        | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3-flash-preview; probe_semantic_warning:google/gemini-3-flash-preview:temporal_arith_003__natural_language; probe_semantic_warning:google/gemini-3-flash-preview:multi_hop_010__natural_language |
| med_reasoning       | openai/gpt-5.4                       | reasoning     | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,presence_penalty,reasoning,response_format,seed,stop,structured_outputs,tool_choice,tools,top_logprobs; probe_semantic_warning:openai/gpt-5.4:temporal_arith_003__natural_language                                                                                                     |
| large_reasoning     | google/gemini-3.1-pro-preview        | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3.1-pro-preview; probe_semantic_warning:google/gemini-3.1-pro-preview:temporal_arith_003__natural_language                                                                                       |

## Headline Format Comparison
| Format           | Accuracy | 95% CI           | Syntactic | Calendar | Compliance | Clean  |
| ---------------- | -------- | ---------------- | --------- | -------- | ---------- | ------ |
| iso_8601         | 92.74%   | 90.78% to 94.31% | 99.64%    | -        | 0.991      | 96.90% |
| natural_language | 86.67%   | 84.20% to 88.80% | 99.64%    | 90.00%   | 0.945      | 97.38% |
| rfc_2822         | 88.57%   | 86.24% to 90.55% | 99.52%    | 91.39%   | 0.975      | 95.36% |

## Primary Results
| task_type                  | format           | large_non_reasoning | large_reasoning | med_non_reasoning | med_reasoning | small_non_reasoning | small_reasoning |
| -------------------------- | ---------------- | ------------------- | --------------- | ----------------- | ------------- | ------------------- | --------------- |
| direct_generation          | iso_8601         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation          | natural_language | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation          | rfc_2822         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| edge_cases                 | iso_8601         | 90.0                | 80.0            | 90.0              | 80.0          | 75.0                | 75.0            |
| edge_cases                 | natural_language | 80.0                | 75.0            | 80.0              | 80.0          | 85.0                | 75.0            |
| edge_cases                 | rfc_2822         | 90.0                | 80.0            | 80.0              | 80.0          | 75.0                | 75.0            |
| extraction_from_passage    | iso_8601         | 95.0                | 85.0            | 95.0              | 100.0         | 85.0                | 95.0            |
| extraction_from_passage    | natural_language | 95.0                | 95.0            | 100.0             | 100.0         | 85.0                | 90.0            |
| extraction_from_passage    | rfc_2822         | 95.0                | 100.0           | 95.0              | 100.0         | 80.0                | 95.0            |
| format_conversion          | iso_8601         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| format_conversion          | natural_language | 100.0               | 100.0           | 100.0             | 45.0          | 85.0                | 60.0            |
| format_conversion          | rfc_2822         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| multi_hop_reasoning        | iso_8601         | 95.0                | 100.0           | 85.0              | 100.0         | 85.0                | 90.0            |
| multi_hop_reasoning        | natural_language | 85.0                | 100.0           | 75.0              | 100.0         | 80.0                | 55.0            |
| multi_hop_reasoning        | rfc_2822         | 85.0                | 90.0            | 90.0              | 100.0         | 55.0                | 60.0            |
| multiple_choice_validation | iso_8601         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| multiple_choice_validation | natural_language | 95.0                | 100.0           | 75.0              | 100.0         | 95.0                | 100.0           |
| multiple_choice_validation | rfc_2822         | 100.0               | 100.0           | 65.0              | 100.0         | 100.0               | 100.0           |
| temporal_arithmetic        | iso_8601         | 85.0                | 80.0            | 85.0              | 80.0          | 85.0                | 80.0            |
| temporal_arithmetic        | natural_language | 70.0                | 80.0            | 70.0              | 80.0          | 75.0                | 75.0            |
| temporal_arithmetic        | rfc_2822         | 85.0                | 70.0            | 60.0              | 80.0          | 60.0                | 75.0            |

## Pairwise Format Tests
| Left             | Right            | Test        | p-value     |
| ---------------- | ---------------- | ----------- | ----------- |
| iso_8601         | natural_language | chi_squared | 4.24041e-05 |
| iso_8601         | rfc_2822         | chi_squared | 0.00334895  |
| natural_language | rfc_2822         | chi_squared | 0.235941    |

## Interaction Highlights
| Mode          | Format           | Accuracy | Correct | N   |
| ------------- | ---------------- | -------- | ------- | --- |
| non_reasoning | iso_8601         | 92.86%   | 390     | 420 |
| non_reasoning | natural_language | 87.14%   | 366     | 420 |
| non_reasoning | rfc_2822         | 86.43%   | 363     | 420 |
| reasoning     | iso_8601         | 92.62%   | 389     | 420 |
| reasoning     | natural_language | 86.19%   | 362     | 420 |
| reasoning     | rfc_2822         | 90.71%   | 381     | 420 |

| Size  | Format           | Accuracy | Correct | N   |
| ----- | ---------------- | -------- | ------- | --- |
| large | iso_8601         | 93.57%   | 262     | 280 |
| large | natural_language | 91.07%   | 255     | 280 |
| large | rfc_2822         | 92.50%   | 259     | 280 |
| med   | iso_8601         | 93.93%   | 263     | 280 |
| med   | natural_language | 86.07%   | 241     | 280 |
| med   | rfc_2822         | 89.29%   | 250     | 280 |
| small | iso_8601         | 90.71%   | 254     | 280 |
| small | natural_language | 82.86%   | 232     | 280 |
| small | rfc_2822         | 83.93%   | 235     | 280 |

| Task Type                  | Best Format      | Best Accuracy | Worst Format     | Worst Accuracy | Spread |
| -------------------------- | ---------------- | ------------- | ---------------- | -------------- | ------ |
| format_conversion          | iso_8601         | 100.00%       | natural_language | 81.67%         | 18.33% |
| multi_hop_reasoning        | iso_8601         | 92.50%        | rfc_2822         | 80.00%         | 12.50% |
| temporal_arithmetic        | iso_8601         | 82.50%        | rfc_2822         | 71.67%         | 10.83% |
| multiple_choice_validation | iso_8601         | 100.00%       | rfc_2822         | 94.17%         | 5.83%  |
| edge_cases                 | iso_8601         | 81.67%        | natural_language | 79.17%         | 2.50%  |
| extraction_from_passage    | natural_language | 94.17%        | iso_8601         | 92.50%         | 1.67%  |
| direct_generation          | iso_8601         | 100.00%       | rfc_2822         | 100.00%        | 0.00%  |

## Error Taxonomy
| Format           | Model Cell          | Error Type            | Count |
| ---------------- | ------------------- | --------------------- | ----- |
| iso_8601         | large_non_reasoning | arithmetic_error      | 6     |
| iso_8601         | large_non_reasoning | extraction_error      | 1     |
| iso_8601         | large_reasoning     | arithmetic_error      | 7     |
| iso_8601         | large_reasoning     | extraction_error      | 1     |
| iso_8601         | large_reasoning     | syntax_error          | 3     |
| iso_8601         | med_non_reasoning   | arithmetic_error      | 8     |
| iso_8601         | med_non_reasoning   | extraction_error      | 1     |
| iso_8601         | med_reasoning       | arithmetic_error      | 8     |
| iso_8601         | small_non_reasoning | arithmetic_error      | 9     |
| iso_8601         | small_non_reasoning | extraction_error      | 3     |
| iso_8601         | small_non_reasoning | timezone_error        | 2     |
| iso_8601         | small_reasoning     | arithmetic_error      | 10    |
| iso_8601         | small_reasoning     | extraction_error      | 1     |
| iso_8601         | small_reasoning     | timezone_error        | 1     |
| natural_language | large_non_reasoning | arithmetic_error      | 9     |
| natural_language | large_non_reasoning | day_of_week_error     | 4     |
| natural_language | large_non_reasoning | extraction_error      | 1     |
| natural_language | large_non_reasoning | unknown               | 1     |
| natural_language | large_reasoning     | arithmetic_error      | 7     |
| natural_language | large_reasoning     | instruction_violation | 1     |
| natural_language | large_reasoning     | syntax_error          | 2     |
| natural_language | med_non_reasoning   | arithmetic_error      | 2     |
| natural_language | med_non_reasoning   | day_of_week_error     | 10    |
| natural_language | med_non_reasoning   | timezone_error        | 3     |
| natural_language | med_non_reasoning   | unknown               | 5     |
| natural_language | med_reasoning       | arithmetic_error      | 8     |
| natural_language | med_reasoning       | timezone_error        | 11    |
| natural_language | small_non_reasoning | arithmetic_error      | 6     |
| natural_language | small_non_reasoning | day_of_week_error     | 5     |
| natural_language | small_non_reasoning | extraction_error      | 3     |

Truncated in summary; full table is in `error_taxonomy.csv`.

## Cost Report
| Category   | Name                       | Cost USD | Reason |
| ---------- | -------------------------- | -------- | ------ |
| total      | all                        | 7.454499 |        |
| model_cell | large_non_reasoning        | 0.717057 |        |
| model_cell | large_reasoning            | 4.441421 |        |
| model_cell | med_non_reasoning          | 0.42865  |        |
| model_cell | med_reasoning              | 1.769825 |        |
| model_cell | small_non_reasoning        | 0.032646 |        |
| model_cell | small_reasoning            | 0.0649   |        |
| task_type  | direct_generation          | 0.72385  |        |
| task_type  | edge_cases                 | 1.109545 |        |
| task_type  | extraction_from_passage    | 1.561053 |        |
| task_type  | format_conversion          | 0.680462 |        |
| task_type  | multi_hop_reasoning        | 1.490123 |        |
| task_type  | multiple_choice_validation | 0.631855 |        |
| task_type  | temporal_arithmetic        | 1.257611 |        |

## Recommendations
- Highest overall reliability: `iso_8601` at 92.74% with 95% CI 90.78% to 94.31%.
- `iso_8601` vs `natural_language`: chi_squared p-value = 4.24041e-05.
- `iso_8601` vs `rfc_2822`: chi_squared p-value = 0.00334895.
- Size `large` ranking: iso_8601 93.57%, rfc_2822 92.50%, natural_language 91.07%.
- Size `med` ranking: iso_8601 93.93%, rfc_2822 89.29%, natural_language 86.07%.
- Size `small` ranking: iso_8601 90.71%, rfc_2822 83.93%, natural_language 82.86%.
- Reasoning delta for `iso_8601`: 92.62% vs 92.86% (`+-0.24` points).
- Reasoning delta for `natural_language`: 86.19% vs 87.14% (`+-0.95` points).
- Reasoning delta for `rfc_2822`: 90.71% vs 86.43% (`+4.29` points).
- Most format-sensitive tasks: `format_conversion` (iso_8601 100.00% vs natural_language 81.67%); `multi_hop_reasoning` (iso_8601 92.50% vs rfc_2822 80.00%); `temporal_arithmetic` (iso_8601 82.50% vs rfc_2822 71.67%).
- System-prompt recommendation: Use `ISO 8601` for system-prompted timestamp generation when you want the best first-attempt reliability.
- Common `iso_8601` error modes: arithmetic_error (48), extraction_error (7), syntax_error (3).
- Common `natural_language` error modes: arithmetic_error (41), day_of_week_error (28), timezone_error (27).
- Common `rfc_2822` error modes: arithmetic_error (46), day_of_week_error (29), extraction_error (7).
- Total benchmark spend: $7.454499.
