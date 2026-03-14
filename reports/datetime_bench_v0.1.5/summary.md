# Datetime Format Benchmark Summary

## Model Selection
| Cell                | Selected Model                       | Mode          | Notes                                                                                                                                                                                                |
| ------------------- | ------------------------------------ | ------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| small_non_reasoning | google/gemini-3.1-flash-lite-preview | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3.1-flash-lite-preview |
| med_non_reasoning   | anthropic/claude-sonnet-4.6          | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                              |
| large_non_reasoning | anthropic/claude-opus-4.6            | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                              |
| small_reasoning     | google/gemini-3-flash-preview        | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3-flash-preview        |
| med_reasoning       | openai/gpt-5.4                       | reasoning     | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,presence_penalty,reasoning,response_format,seed,stop,structured_outputs,tool_choice,tools,top_logprobs       |
| large_reasoning     | google/gemini-3.1-pro-preview        | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3.1-pro-preview        |

## Headline Format Comparison
| Format           | Accuracy | 95% CI           | Syntactic | Calendar | Compliance | Clean  |
| ---------------- | -------- | ---------------- | --------- | -------- | ---------- | ------ |
| iso_8601         | 92.86%   | 90.91% to 94.41% | 99.88%    | -        | 0.993      | 96.90% |
| javascript_date  | 88.81%   | 86.50% to 90.77% | 100.00%   | 89.03%   | 0.970      | 97.86% |
| natural_language | 86.43%   | 83.95% to 88.58% | 99.64%    | 90.42%   | 0.952      | 97.38% |
| python_datetime  | 93.81%   | 91.97% to 95.25% | 100.00%   | -        | 0.995      | 97.74% |
| rfc_2822         | 90.00%   | 87.79% to 91.85% | 100.00%   | 92.36%   | 0.986      | 95.24% |
| rfc_3339         | 93.21%   | 91.31% to 94.73% | 100.00%   | -        | 0.987      | 97.02% |

## Primary Results
| task_type               | format           | large_non_reasoning | large_reasoning | med_non_reasoning | med_reasoning | small_non_reasoning | small_reasoning |
| ----------------------- | ---------------- | ------------------- | --------------- | ----------------- | ------------- | ------------------- | --------------- |
| direct_generation       | iso_8601         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation       | javascript_date  | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation       | natural_language | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation       | python_datetime  | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation       | rfc_2822         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation       | rfc_3339         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| edge_cases              | iso_8601         | 90.0                | 80.0            | 90.0              | 80.0          | 75.0                | 75.0            |
| edge_cases              | javascript_date  | 90.0                | 80.0            | 90.0              | 80.0          | 80.0                | 80.0            |
| edge_cases              | natural_language | 80.0                | 80.0            | 75.0              | 80.0          | 85.0                | 75.0            |
| edge_cases              | python_datetime  | 80.0                | 85.0            | 95.0              | 100.0         | 75.0                | 75.0            |
| edge_cases              | rfc_2822         | 90.0                | 85.0            | 80.0              | 80.0          | 75.0                | 75.0            |
| edge_cases              | rfc_3339         | 90.0                | 80.0            | 90.0              | 80.0          | 75.0                | 75.0            |
| extraction_from_passage | iso_8601         | 95.0                | 90.0            | 95.0              | 100.0         | 85.0                | 95.0            |
| extraction_from_passage | javascript_date  | 95.0                | 95.0            | 85.0              | 100.0         | 85.0                | 100.0           |
| extraction_from_passage | natural_language | 95.0                | 95.0            | 100.0             | 100.0         | 85.0                | 95.0            |
| extraction_from_passage | python_datetime  | 90.0                | 95.0            | 90.0              | 100.0         | 85.0                | 95.0            |
| extraction_from_passage | rfc_2822         | 95.0                | 100.0           | 95.0              | 100.0         | 80.0                | 100.0           |
| extraction_from_passage | rfc_3339         | 95.0                | 95.0            | 95.0              | 100.0         | 90.0                | 100.0           |
| format_conversion       | iso_8601         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| format_conversion       | javascript_date  | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| format_conversion       | natural_language | 95.0                | 100.0           | 85.0              | 40.0          | 90.0                | 60.0            |
| format_conversion       | python_datetime  | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| format_conversion       | rfc_2822         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| format_conversion       | rfc_3339         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| multi_hop_reasoning     | iso_8601         | 95.0                | 100.0           | 85.0              | 100.0         | 85.0                | 90.0            |
| multi_hop_reasoning     | javascript_date  | 75.0                | 100.0           | 55.0              | 100.0         | 80.0                | 75.0            |
| multi_hop_reasoning     | natural_language | 85.0                | 100.0           | 70.0              | 95.0          | 80.0                | 55.0            |
| multi_hop_reasoning     | python_datetime  | 95.0                | 100.0           | 80.0              | 100.0         | 90.0                | 100.0           |
| multi_hop_reasoning     | rfc_2822         | 85.0                | 100.0           | 90.0              | 100.0         | 55.0                | 60.0            |
| multi_hop_reasoning     | rfc_3339         | 95.0                | 100.0           | 85.0              | 100.0         | 85.0                | 90.0            |

Truncated in summary; full table is in `primary_results.csv`.

## Pairwise Format Tests
| Left             | Right            | Test        | p-value     |
| ---------------- | ---------------- | ----------- | ----------- |
| iso_8601         | javascript_date  | chi_squared | 0.00404383  |
| iso_8601         | natural_language | chi_squared | 1.53394e-05 |
| iso_8601         | python_datetime  | chi_squared | 0.433944    |
| iso_8601         | rfc_2822         | chi_squared | 0.0364698   |
| iso_8601         | rfc_3339         | chi_squared | 0.773696    |
| javascript_date  | natural_language | chi_squared | 0.138476    |
| javascript_date  | python_datetime  | chi_squared | 0.000275191 |
| javascript_date  | rfc_2822         | chi_squared | 0.427952    |
| javascript_date  | rfc_3339         | chi_squared | 0.00159841  |
| natural_language | python_datetime  | chi_squared | 3.99738e-07 |
| natural_language | rfc_2822         | chi_squared | 0.0232097   |
| natural_language | rfc_3339         | chi_squared | 4.24019e-06 |
| python_datetime  | rfc_2822         | chi_squared | 0.0042061   |
| python_datetime  | rfc_3339         | chi_squared | 0.620425    |
| rfc_2822         | rfc_3339         | chi_squared | 0.0175162   |

## Interaction Highlights
| Mode          | Format           | Accuracy | Correct | N   |
| ------------- | ---------------- | -------- | ------- | --- |
| non_reasoning | iso_8601         | 92.86%   | 390     | 420 |
| non_reasoning | javascript_date  | 85.24%   | 358     | 420 |
| non_reasoning | natural_language | 86.67%   | 364     | 420 |
| non_reasoning | python_datetime  | 92.86%   | 390     | 420 |
| non_reasoning | rfc_2822         | 87.86%   | 369     | 420 |
| non_reasoning | rfc_3339         | 93.10%   | 391     | 420 |
| reasoning     | iso_8601         | 92.86%   | 390     | 420 |
| reasoning     | javascript_date  | 92.38%   | 388     | 420 |
| reasoning     | natural_language | 86.19%   | 362     | 420 |
| reasoning     | python_datetime  | 94.76%   | 398     | 420 |
| reasoning     | rfc_2822         | 92.14%   | 387     | 420 |
| reasoning     | rfc_3339         | 93.33%   | 392     | 420 |

| Size  | Format           | Accuracy | Correct | N   |
| ----- | ---------------- | -------- | ------- | --- |
| large | iso_8601         | 93.93%   | 263     | 280 |
| large | javascript_date  | 92.14%   | 258     | 280 |
| large | natural_language | 91.79%   | 257     | 280 |
| large | python_datetime  | 93.57%   | 262     | 280 |
| large | rfc_2822         | 93.93%   | 263     | 280 |
| large | rfc_3339         | 94.29%   | 264     | 280 |
| med   | iso_8601         | 93.93%   | 263     | 280 |
| med   | javascript_date  | 85.71%   | 240     | 280 |
| med   | natural_language | 83.57%   | 234     | 280 |
| med   | python_datetime  | 95.71%   | 268     | 280 |
| med   | rfc_2822         | 91.43%   | 256     | 280 |
| med   | rfc_3339         | 93.93%   | 263     | 280 |
| small | iso_8601         | 90.71%   | 254     | 280 |
| small | javascript_date  | 88.57%   | 248     | 280 |
| small | natural_language | 83.93%   | 235     | 280 |
| small | python_datetime  | 92.14%   | 258     | 280 |
| small | rfc_2822         | 84.64%   | 237     | 280 |
| small | rfc_3339         | 91.43%   | 256     | 280 |

| Task Type                  | Best Format     | Best Accuracy | Worst Format     | Worst Accuracy | Spread |
| -------------------------- | --------------- | ------------- | ---------------- | -------------- | ------ |
| format_conversion          | iso_8601        | 100.00%       | natural_language | 78.33%         | 21.67% |
| multi_hop_reasoning        | python_datetime | 94.17%        | natural_language | 80.83%         | 13.33% |
| temporal_arithmetic        | python_datetime | 85.00%        | javascript_date  | 72.50%         | 12.50% |
| multiple_choice_validation | iso_8601        | 100.00%       | javascript_date  | 91.67%         | 8.33%  |
| edge_cases                 | python_datetime | 85.00%        | natural_language | 79.17%         | 5.83%  |
| extraction_from_passage    | rfc_3339        | 95.83%        | python_datetime  | 92.50%         | 3.33%  |
| direct_generation          | iso_8601        | 100.00%       | rfc_3339         | 100.00%        | 0.00%  |

## Error Taxonomy
| Format          | Model Cell          | Error Type        | Count |
| --------------- | ------------------- | ----------------- | ----- |
| iso_8601        | large_non_reasoning | arithmetic_error  | 6     |
| iso_8601        | large_non_reasoning | extraction_error  | 1     |
| iso_8601        | large_reasoning     | arithmetic_error  | 8     |
| iso_8601        | large_reasoning     | extraction_error  | 2     |
| iso_8601        | med_non_reasoning   | arithmetic_error  | 8     |
| iso_8601        | med_non_reasoning   | extraction_error  | 1     |
| iso_8601        | med_reasoning       | arithmetic_error  | 7     |
| iso_8601        | med_reasoning       | syntax_error      | 1     |
| iso_8601        | small_non_reasoning | arithmetic_error  | 9     |
| iso_8601        | small_non_reasoning | extraction_error  | 3     |
| iso_8601        | small_non_reasoning | timezone_error    | 2     |
| iso_8601        | small_reasoning     | arithmetic_error  | 10    |
| iso_8601        | small_reasoning     | extraction_error  | 1     |
| iso_8601        | small_reasoning     | timezone_error    | 1     |
| javascript_date | large_non_reasoning | arithmetic_error  | 6     |
| javascript_date | large_non_reasoning | day_of_week_error | 5     |
| javascript_date | large_non_reasoning | extraction_error  | 1     |
| javascript_date | large_non_reasoning | unknown           | 1     |
| javascript_date | large_reasoning     | arithmetic_error  | 8     |
| javascript_date | large_reasoning     | extraction_error  | 1     |
| javascript_date | med_non_reasoning   | arithmetic_error  | 3     |
| javascript_date | med_non_reasoning   | day_of_week_error | 16    |
| javascript_date | med_non_reasoning   | extraction_error  | 3     |
| javascript_date | med_non_reasoning   | unknown           | 9     |
| javascript_date | med_reasoning       | arithmetic_error  | 9     |
| javascript_date | small_non_reasoning | arithmetic_error  | 9     |
| javascript_date | small_non_reasoning | day_of_week_error | 6     |
| javascript_date | small_non_reasoning | extraction_error  | 3     |
| javascript_date | small_reasoning     | arithmetic_error  | 9     |
| javascript_date | small_reasoning     | day_of_week_error | 5     |

Truncated in summary; full table is in `error_taxonomy.csv`.

## Cost Report
| Category   | Name                       | Cost USD  | Reason |
| ---------- | -------------------------- | --------- | ------ |
| total      | all                        | 15.366276 |        |
| model_cell | large_non_reasoning        | 1.421176  |        |
| model_cell | large_reasoning            | 9.31548   |        |
| model_cell | med_non_reasoning          | 0.855037  |        |
| model_cell | med_reasoning              | 3.572759  |        |
| model_cell | small_non_reasoning        | 0.067664  |        |
| model_cell | small_reasoning            | 0.134161  |        |
| task_type  | direct_generation          | 1.519658  |        |
| task_type  | edge_cases                 | 2.528313  |        |
| task_type  | extraction_from_passage    | 3.062683  |        |
| task_type  | format_conversion          | 1.464427  |        |
| task_type  | multi_hop_reasoning        | 3.049672  |        |
| task_type  | multiple_choice_validation | 1.189798  |        |
| task_type  | temporal_arithmetic        | 2.551726  |        |

## Recommendations
- Highest overall reliability: `python_datetime` at 93.81% with 95% CI 91.97% to 95.25%.
- `python_datetime` vs `iso_8601`: chi_squared p-value = 0.433944.
- `python_datetime` vs `javascript_date`: chi_squared p-value = 0.000275191.
- `python_datetime` vs `natural_language`: chi_squared p-value = 3.99738e-07.
- `python_datetime` vs `rfc_2822`: chi_squared p-value = 0.0042061.
- `python_datetime` vs `rfc_3339`: chi_squared p-value = 0.620425.
- Size `large` ranking: rfc_3339 94.29%, iso_8601 93.93%, rfc_2822 93.93%, python_datetime 93.57%, javascript_date 92.14%, natural_language 91.79%.
- Size `med` ranking: python_datetime 95.71%, iso_8601 93.93%, rfc_3339 93.93%, rfc_2822 91.43%, javascript_date 85.71%, natural_language 83.57%.
- Size `small` ranking: python_datetime 92.14%, rfc_3339 91.43%, iso_8601 90.71%, javascript_date 88.57%, rfc_2822 84.64%, natural_language 83.93%.
- Reasoning delta for `iso_8601`: 92.86% vs 92.86% (`+0.00` points).
- Reasoning delta for `javascript_date`: 92.38% vs 85.24% (`+7.14` points).
- Reasoning delta for `natural_language`: 86.19% vs 86.67% (`+-0.48` points).
- Reasoning delta for `python_datetime`: 94.76% vs 92.86% (`+1.90` points).
- Reasoning delta for `rfc_2822`: 92.14% vs 87.86% (`+4.29` points).
- Reasoning delta for `rfc_3339`: 93.33% vs 93.10% (`+0.24` points).
- Most format-sensitive tasks: `format_conversion` (iso_8601 100.00% vs natural_language 78.33%); `multi_hop_reasoning` (python_datetime 94.17% vs natural_language 80.83%); `temporal_arithmetic` (python_datetime 85.00% vs javascript_date 72.50%).
- System-prompt recommendation: Use the top-ranked format from the benchmark for system-prompted timestamp generation.
- Common `iso_8601` error modes: arithmetic_error (48), extraction_error (8), timezone_error (3).
- Common `javascript_date` error modes: arithmetic_error (44), day_of_week_error (32), unknown (10).
- Common `natural_language` error modes: arithmetic_error (44), timezone_error (29), day_of_week_error (28).
- Common `python_datetime` error modes: arithmetic_error (41), extraction_error (9), timezone_error (2).
- Common `rfc_2822` error modes: arithmetic_error (46), day_of_week_error (27), extraction_error (6).
- Common `rfc_3339` error modes: arithmetic_error (50), extraction_error (5), timezone_error (2).
- Total benchmark spend: $15.366276.
