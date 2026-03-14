# Datetime Format Benchmark Summary

## Run Metadata
| Field            | Value                                    |
| ---------------- | ---------------------------------------- |
| Version          | v0.2                                     |
| Previous Version | v0.1.5                                   |
| Run Slug         | datetime_bench_v0.2                      |
| Report Slug      | datetime_bench_v0.2                      |
| Seed             | 42                                       |
| Max Tokens       | 300                                      |
| Soft Cap USD     | 250.0                                    |
| Hard Cap USD     | 300.0                                    |
| Resume           | True                                     |
| Dry Run Cached   | False                                    |
| Git SHA          | 4a84df9afadb9c909bb092ec4aae68f025170304 |

## Model Selection
| Cell                | Selected Model                       | Mode          | Notes                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| ------------------- | ------------------------------------ | ------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| small_non_reasoning | google/gemini-3.1-flash-lite-preview | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3.1-flash-lite-preview                                                                                                                                                                                                                                       |
| med_non_reasoning   | anthropic/claude-sonnet-4.6          | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                                                                                                                                                                                                                                                                    |
| large_non_reasoning | anthropic/claude-opus-4.6            | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                                                                                                                                                                                                                                                                    |
| small_reasoning     | google/gemini-3-flash-preview        | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3-flash-preview                                                                                                                                                                                                                                              |
| med_reasoning       | anthropic/claude-sonnet-4.6          | reasoning     | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,presence_penalty,reasoning,response_format,seed,stop,structured_outputs,tool_choice,tools,top_logprobs; probe_incompatible:openai/gpt-5.4:temporal_arith_035__natural_language:syntactic=False:semantic=False; probe_semantic_warning:anthropic/claude-sonnet-4.6:temporal_arith_035__natural_language; probe_fallback:anthropic/claude-sonnet-4.6 |
| large_reasoning     | anthropic/claude-opus-4.6            | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3.1-pro-preview; probe_incompatible:google/gemini-3.1-pro-preview:temporal_arith_035__natural_language:syntactic=False:semantic=False; probe_fallback:anthropic/claude-opus-4.6                                                                              |

## Headline Format Comparison
| Format           | Accuracy | Strict | 95% CI           | Syntactic | Calendar | Compliance | Clean  |
| ---------------- | -------- | ------ | ---------------- | --------- | -------- | ---------- | ------ |
| iso_8601         | 90.50%   | 90.50% | 88.85% to 91.92% | 99.57%    | -        | 0.983      | 96.31% |
| javascript_date  | 86.38%   | 80.78% | 84.49% to 88.07% | 99.57%    | 86.43%   | 0.905      | 96.67% |
| natural_language | 84.33%   | 79.86% | 82.34% to 86.13% | 99.86%    | 87.14%   | 0.939      | 97.52% |
| python_datetime  | 90.85%   | 90.85% | 89.23% to 92.25% | 99.72%    | -        | 0.984      | 97.02% |
| rfc_2822         | 86.17%   | 82.48% | 84.27% to 87.87% | 99.08%    | 87.94%   | 0.960      | 94.04% |
| rfc_3339         | 90.99%   | 90.99% | 89.39% to 92.38% | 99.57%    | -        | 0.976      | 95.39% |
| unix_epoch       | 39.86%   | 39.86% | 37.33% to 42.44% | 87.87%    | -        | 0.694      | 85.39% |

## Primary Results
| task_type               | format           | large_non_reasoning | large_reasoning | med_non_reasoning | med_reasoning | small_non_reasoning | small_reasoning |
| ----------------------- | ---------------- | ------------------- | --------------- | ----------------- | ------------- | ------------------- | --------------- |
| direct_generation       | iso_8601         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 97.14           |
| direct_generation       | javascript_date  | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 94.29           |
| direct_generation       | natural_language | 100.0               | 100.0           | 100.0             | 100.0         | 85.71               | 94.29           |
| direct_generation       | python_datetime  | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation       | rfc_2822         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 91.43           |
| direct_generation       | rfc_3339         | 100.0               | 100.0           | 100.0             | 100.0         | 100.0               | 100.0           |
| direct_generation       | unix_epoch       | 22.86               | 40.0            | 22.86             | 68.57         | 40.0                | 71.43           |
| edge_cases              | iso_8601         | 94.29               | 82.86           | 91.43             | 85.71         | 80.0                | 80.0            |
| edge_cases              | javascript_date  | 94.29               | 88.57           | 94.29             | 80.0          | 82.86               | 77.14           |
| edge_cases              | natural_language | 82.86               | 85.71           | 77.14             | 88.57         | 88.57               | 71.43           |
| edge_cases              | python_datetime  | 82.86               | 88.57           | 97.14             | 97.14         | 80.0                | 80.0            |
| edge_cases              | rfc_2822         | 94.29               | 85.71           | 80.0              | 88.57         | 77.14               | 74.29           |
| edge_cases              | rfc_3339         | 94.29               | 85.71           | 91.43             | 88.57         | 80.0                | 80.0            |
| edge_cases              | unix_epoch       | 8.57                | 57.14           | 8.57              | 71.43         | 11.43               | 60.0            |
| extraction_from_passage | iso_8601         | 83.33               | 93.33           | 73.33             | 90.0          | 60.0                | 83.33           |
| extraction_from_passage | javascript_date  | 90.0                | 90.0            | 73.33             | 83.33         | 66.67               | 80.0            |
| extraction_from_passage | natural_language | 80.0                | 90.0            | 90.0              | 83.33         | 66.67               | 90.0            |
| extraction_from_passage | python_datetime  | 83.33               | 90.0            | 70.0              | 83.33         | 63.33               | 90.0            |
| extraction_from_passage | rfc_2822         | 83.33               | 90.0            | 76.67             | 80.0          | 63.33               | 96.67           |
| extraction_from_passage | rfc_3339         | 80.0                | 90.0            | 76.67             | 83.33         | 60.0                | 93.33           |
| extraction_from_passage | unix_epoch       | 16.67               | 53.33           | 30.0              | 76.67         | 16.67               | 46.67           |
| format_conversion       | iso_8601         | 85.71               | 91.43           | 88.57             | 91.43         | 97.14               | 94.29           |
| format_conversion       | javascript_date  | 91.43               | 97.14           | 91.43             | 88.57         | 91.43               | 94.29           |
| format_conversion       | natural_language | 77.14               | 85.71           | 65.71             | 80.0          | 68.57               | 68.57           |
| format_conversion       | python_datetime  | 82.86               | 97.14           | 82.86             | 88.57         | 88.57               | 94.29           |
| format_conversion       | rfc_2822         | 85.71               | 91.43           | 82.86             | 82.86         | 94.29               | 94.29           |
| format_conversion       | rfc_3339         | 88.57               | 97.14           | 88.57             | 88.57         | 88.57               | 94.29           |
| format_conversion       | unix_epoch       | 25.71               | 65.71           | 22.86             | 88.57         | 31.43               | 77.14           |
| multi_hop_reasoning     | iso_8601         | 97.14               | 100.0           | 77.14             | 100.0         | 91.43               | 91.43           |
| multi_hop_reasoning     | javascript_date  | 82.86               | 97.14           | 51.43             | 100.0         | 82.86               | 77.14           |

Truncated in summary; full table is in `primary_results.csv`.

## Pairwise Format Tests
| Left             | Right            | Test        | p-value      |
| ---------------- | ---------------- | ----------- | ------------ |
| iso_8601         | javascript_date  | chi_squared | 0.000635893  |
| iso_8601         | natural_language | chi_squared | 7.8606e-07   |
| iso_8601         | python_datetime  | chi_squared | 0.746104     |
| iso_8601         | rfc_2822         | chi_squared | 0.000345915  |
| iso_8601         | rfc_3339         | chi_squared | 0.649218     |
| iso_8601         | unix_epoch       | chi_squared | 3.10404e-175 |
| javascript_date  | natural_language | chi_squared | 0.122449     |
| javascript_date  | python_datetime  | chi_squared | 0.000187466  |
| javascript_date  | rfc_2822         | chi_squared | 0.86959      |
| javascript_date  | rfc_3339         | chi_squared | 0.000111348  |
| javascript_date  | unix_epoch       | chi_squared | 1.38958e-144 |
| natural_language | python_datetime  | chi_squared | 1.48442e-07  |
| natural_language | rfc_2822         | chi_squared | 0.167386     |
| natural_language | rfc_3339         | chi_squared | 7.36888e-08  |
| natural_language | unix_epoch       | chi_squared | 8.03479e-131 |
| python_datetime  | rfc_2822         | chi_squared | 9.72356e-05  |
| python_datetime  | rfc_3339         | chi_squared | 0.895703     |
| python_datetime  | unix_epoch       | chi_squared | 4.3469e-178  |
| rfc_2822         | rfc_3339         | chi_squared | 5.66543e-05  |
| rfc_2822         | unix_epoch       | chi_squared | 4.09635e-143 |
| rfc_3339         | unix_epoch       | chi_squared | 3.06706e-179 |

## Interaction Highlights
| Mode          | Format           | Accuracy | Strict | Correct | N   |
| ------------- | ---------------- | -------- | ------ | ------- | --- |
| non_reasoning | iso_8601         | 88.94%   | 88.94% | 627     | 705 |
| non_reasoning | javascript_date  | 83.40%   | 75.18% | 588     | 705 |
| non_reasoning | natural_language | 80.57%   | 73.05% | 568     | 705 |
| non_reasoning | python_datetime  | 87.66%   | 87.66% | 618     | 705 |
| non_reasoning | rfc_2822         | 83.40%   | 77.16% | 588     | 705 |
| non_reasoning | rfc_3339         | 88.94%   | 88.94% | 627     | 705 |
| non_reasoning | unix_epoch       | 19.86%   | 19.86% | 140     | 705 |
| reasoning     | iso_8601         | 92.06%   | 92.06% | 649     | 705 |
| reasoning     | javascript_date  | 89.36%   | 86.38% | 630     | 705 |
| reasoning     | natural_language | 88.09%   | 86.67% | 621     | 705 |
| reasoning     | python_datetime  | 94.04%   | 94.04% | 663     | 705 |
| reasoning     | rfc_2822         | 88.94%   | 87.80% | 627     | 705 |
| reasoning     | rfc_3339         | 93.05%   | 93.05% | 656     | 705 |
| reasoning     | unix_epoch       | 59.86%   | 59.86% | 422     | 705 |

| Size  | Format           | Accuracy | Strict | Correct | N   |
| ----- | ---------------- | -------- | ------ | ------- | --- |
| large | iso_8601         | 92.55%   | 92.55% | 435     | 470 |
| large | javascript_date  | 92.34%   | 88.51% | 434     | 470 |
| large | natural_language | 88.94%   | 86.17% | 418     | 470 |
| large | python_datetime  | 91.91%   | 91.91% | 432     | 470 |
| large | rfc_2822         | 90.43%   | 88.51% | 425     | 470 |
| large | rfc_3339         | 92.77%   | 92.77% | 436     | 470 |
| large | unix_epoch       | 37.02%   | 37.02% | 174     | 470 |
| med   | iso_8601         | 89.79%   | 89.79% | 422     | 470 |
| med   | javascript_date  | 81.70%   | 74.68% | 384     | 470 |
| med   | natural_language | 84.04%   | 77.66% | 395     | 470 |
| med   | python_datetime  | 90.43%   | 90.43% | 425     | 470 |
| med   | rfc_2822         | 86.17%   | 80.21% | 405     | 470 |
| med   | rfc_3339         | 90.64%   | 90.64% | 426     | 470 |
| med   | unix_epoch       | 44.04%   | 44.04% | 207     | 470 |
| small | iso_8601         | 89.15%   | 89.15% | 419     | 470 |
| small | javascript_date  | 85.11%   | 79.15% | 400     | 470 |
| small | natural_language | 80.00%   | 75.74% | 376     | 470 |
| small | python_datetime  | 90.21%   | 90.21% | 424     | 470 |
| small | rfc_2822         | 81.91%   | 78.72% | 385     | 470 |
| small | rfc_3339         | 89.57%   | 89.57% | 421     | 470 |
| small | unix_epoch       | 38.51%   | 38.51% | 181     | 470 |

| Task Type                  | Best Format      | Best Accuracy | Worst Format | Worst Accuracy | Spread |
| -------------------------- | ---------------- | ------------- | ------------ | -------------- | ------ |
| multi_hop_reasoning        | python_datetime  | 93.81%        | unix_epoch   | 21.90%         | 71.90% |
| temporal_arithmetic        | python_datetime  | 87.50%        | unix_epoch   | 24.58%         | 62.92% |
| direct_generation          | python_datetime  | 100.00%       | unix_epoch   | 44.29%         | 55.71% |
| edge_cases                 | python_datetime  | 87.62%        | unix_epoch   | 36.19%         | 51.43% |
| extraction_from_passage    | natural_language | 83.33%        | unix_epoch   | 40.00%         | 43.33% |
| format_conversion          | javascript_date  | 92.38%        | unix_epoch   | 51.90%         | 40.48% |
| multiple_choice_validation | iso_8601         | 100.00%       | unix_epoch   | 71.33%         | 28.67% |

## Error Taxonomy
| Format          | Model Cell          | Error Type            | Count |
| --------------- | ------------------- | --------------------- | ----- |
| iso_8601        | large_non_reasoning | arithmetic_error      | 6     |
| iso_8601        | large_non_reasoning | extraction_error      | 5     |
| iso_8601        | large_non_reasoning | instruction_violation | 4     |
| iso_8601        | large_non_reasoning | unknown               | 5     |
| iso_8601        | large_reasoning     | arithmetic_error      | 10    |
| iso_8601        | large_reasoning     | extraction_error      | 2     |
| iso_8601        | large_reasoning     | unknown               | 3     |
| iso_8601        | med_non_reasoning   | arithmetic_error      | 16    |
| iso_8601        | med_non_reasoning   | extraction_error      | 8     |
| iso_8601        | med_non_reasoning   | instruction_violation | 2     |
| iso_8601        | med_non_reasoning   | unknown               | 4     |
| iso_8601        | med_reasoning       | arithmetic_error      | 12    |
| iso_8601        | med_reasoning       | extraction_error      | 3     |
| iso_8601        | med_reasoning       | unknown               | 3     |
| iso_8601        | small_non_reasoning | arithmetic_error      | 12    |
| iso_8601        | small_non_reasoning | extraction_error      | 12    |
| iso_8601        | small_non_reasoning | timezone_error        | 3     |
| iso_8601        | small_non_reasoning | unknown               | 1     |
| iso_8601        | small_reasoning     | arithmetic_error      | 14    |
| iso_8601        | small_reasoning     | extraction_error      | 5     |
| iso_8601        | small_reasoning     | timezone_error        | 2     |
| iso_8601        | small_reasoning     | unknown               | 2     |
| javascript_date | large_non_reasoning | arithmetic_error      | 8     |
| javascript_date | large_non_reasoning | day_of_week_error     | 6     |
| javascript_date | large_non_reasoning | extraction_error      | 2     |
| javascript_date | large_non_reasoning | instruction_violation | 4     |
| javascript_date | large_non_reasoning | unknown               | 2     |
| javascript_date | large_reasoning     | arithmetic_error      | 9     |
| javascript_date | large_reasoning     | extraction_error      | 3     |
| javascript_date | large_reasoning     | unknown               | 2     |

Truncated in summary; full table is in `error_taxonomy.csv`.

## Cost Report
| Category   | Name                       | Cost USD  | Reason |
| ---------- | -------------------------- | --------- | ------ |
| total      | all                        | 26.388947 |        |
| model_cell | large_non_reasoning        | 3.288138  |        |
| model_cell | large_reasoning            | 12.937504 |        |
| model_cell | med_non_reasoning          | 2.13557   |        |
| model_cell | med_reasoning              | 7.652423  |        |
| model_cell | small_non_reasoning        | 0.125832  |        |
| model_cell | small_reasoning            | 0.249481  |        |
| task_type  | direct_generation          | 2.748784  |        |
| task_type  | edge_cases                 | 3.498952  |        |
| task_type  | extraction_from_passage    | 3.233283  |        |
| task_type  | format_conversion          | 3.755426  |        |
| task_type  | multi_hop_reasoning        | 4.673437  |        |
| task_type  | multiple_choice_validation | 2.260115  |        |
| task_type  | temporal_arithmetic        | 6.218951  |        |

## Recommendations
- Highest overall reliability: `rfc_3339` at 90.99% with 95% CI 89.39% to 92.38%.
- `rfc_3339` vs `iso_8601`: chi_squared p-value = 0.649218.
- `rfc_3339` vs `javascript_date`: chi_squared p-value = 0.000111348.
- `rfc_3339` vs `natural_language`: chi_squared p-value = 7.36888e-08.
- `rfc_3339` vs `python_datetime`: chi_squared p-value = 0.895703.
- `rfc_3339` vs `rfc_2822`: chi_squared p-value = 5.66543e-05.
- `rfc_3339` vs `unix_epoch`: chi_squared p-value = 3.06706e-179.
- Size `large` ranking: rfc_3339 92.77%, iso_8601 92.55%, javascript_date 92.34%, python_datetime 91.91%, rfc_2822 90.43%, natural_language 88.94%, unix_epoch 37.02%.
- Size `med` ranking: rfc_3339 90.64%, python_datetime 90.43%, iso_8601 89.79%, rfc_2822 86.17%, natural_language 84.04%, javascript_date 81.70%, unix_epoch 44.04%.
- Size `small` ranking: python_datetime 90.21%, rfc_3339 89.57%, iso_8601 89.15%, javascript_date 85.11%, rfc_2822 81.91%, natural_language 80.00%, unix_epoch 38.51%.
- Reasoning delta for `iso_8601`: 92.06% vs 88.94% (`+3.12` points).
- Reasoning delta for `javascript_date`: 89.36% vs 83.40% (`+5.96` points).
- Reasoning delta for `natural_language`: 88.09% vs 80.57% (`+7.52` points).
- Reasoning delta for `python_datetime`: 94.04% vs 87.66% (`+6.38` points).
- Reasoning delta for `rfc_2822`: 88.94% vs 83.40% (`+5.53` points).
- Reasoning delta for `rfc_3339`: 93.05% vs 88.94% (`+4.11` points).
- Reasoning delta for `unix_epoch`: 59.86% vs 19.86% (`+40.00` points).
- Most format-sensitive tasks: `multi_hop_reasoning` (python_datetime 93.81% vs unix_epoch 21.90%); `temporal_arithmetic` (python_datetime 87.50% vs unix_epoch 24.58%); `direct_generation` (python_datetime 100.00% vs unix_epoch 44.29%).
- System-prompt recommendation: Use the top-ranked format from the benchmark for system-prompted timestamp generation.
- Common `iso_8601` error modes: arithmetic_error (70), extraction_error (35), unknown (18).
- Common `javascript_date` error modes: day_of_week_error (66), arithmetic_error (54), extraction_error (34).
- Common `natural_language` error modes: day_of_week_error (82), arithmetic_error (52), timezone_error (40).
- Common `python_datetime` error modes: arithmetic_error (60), extraction_error (36), unknown (24).
- Common `rfc_2822` error modes: day_of_week_error (70), arithmetic_error (51), extraction_error (33).
- Common `rfc_3339` error modes: arithmetic_error (65), extraction_error (35), unknown (19).
- Common `unix_epoch` error modes: epoch_conversion_error (543), instruction_violation (155), extraction_error (99).
- Total benchmark spend: $26.388947.
