# Datetime Format Benchmark Summary

## Run Metadata
| Field            | Value                                    |
| ---------------- | ---------------------------------------- |
| Version          | v0.3                                     |
| Previous Version | v0.2                                     |
| Run Slug         | datetime_bench_v0.3                      |
| Report Slug      | datetime_bench_v0.3                      |
| Seed             | 42                                       |
| Max Tokens       | 2500                                     |
| Soft Cap USD     | 250.0                                    |
| Hard Cap USD     | 300.0                                    |
| Resume           | True                                     |
| Dry Run Cached   | True                                     |
| Git SHA          | efaa37a360ead55c47fb2db9ac6e4231d85f2c34 |

## Model Selection
| Cell               | Selected Model                       | Mode          | Notes                                                                                                                                                                                                                                                                                                                                               |
| ------------------ | ------------------------------------ | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| google_small_nr    | google/gemini-3.1-flash-lite-preview | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3.1-flash-lite-preview                                                                                                                                                |
| google_small_r     | google/gemini-3-flash-preview        | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3-flash-preview                                                                                                                                                       |
| google_med_nr      | google/gemini-3-flash-preview        | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3-flash-preview                                                                                                                                                       |
| google_med_r       | google/gemini-3-flash-preview        | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p; selected_fallback:google/gemini-3-flash-preview; probe_semantic_warning:google/gemini-3-flash-preview:extract_026__iso_8601                                                                           |
| google_large_nr    | google/gemini-3.1-pro-preview        | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p                                                                                                                                                                                                        |
| google_large_r     | google/gemini-3.1-pro-preview        | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_p                                                                                                                                                                                                        |
| anthropic_small_nr | anthropic/claude-haiku-4.5           | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p                                                                                                                                                                                                       |
| anthropic_small_r  | anthropic/claude-haiku-4.5           | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p; probe_semantic_warning:anthropic/claude-haiku-4.5:extract_026__iso_8601                                                                                                                              |
| anthropic_med_nr   | anthropic/claude-sonnet-4.6          | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                                                                                                                                                                             |
| anthropic_med_r    | anthropic/claude-sonnet-4.6          | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                                                                                                                                                                             |
| anthropic_large_nr | anthropic/claude-opus-4.6            | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                                                                                                                                                                             |
| anthropic_large_r  | anthropic/claude-opus-4.6            | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_p,verbosity                                                                                                                                                                                             |
| openai_small_nr    | openai/gpt-5-mini                    | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,structured_outputs,tool_choice,tools                                                                                                                                                                                                                               |
| openai_small_r     | openai/gpt-5-mini                    | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,structured_outputs,tool_choice,tools                                                                                                                                                                                                                               |
| openai_med_nr      | openai/gpt-5.1                       | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,structured_outputs,tool_choice,tools                                                                                                                                                                                                                               |
| openai_med_nr_chat | openai/gpt-5.3-chat                  | non_reasoning | supported_parameters=max_tokens,response_format,seed,structured_outputs,tool_choice,tools; selected_fallback:openai/gpt-5.3-chat                                                                                                                                                                                                                    |
| openai_med_r       | openai/gpt-5.4                       | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,structured_outputs,tool_choice,tools                                                                                                                                                                                                                               |
| openai_large_nr    | openai/gpt-5.4                       | non_reasoning | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,structured_outputs,tool_choice,tools                                                                                                                                                                                                                               |
| openai_large_r     | openai/gpt-5.4                       | reasoning     | supported_parameters=include_reasoning,max_tokens,reasoning,response_format,seed,structured_outputs,tool_choice,tools                                                                                                                                                                                                                               |
| qwen_small_nr      | qwen/qwen3.5-9b                      | non_reasoning | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,min_p,presence_penalty,reasoning,repetition_penalty,response_format,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_logprobs,top_p                                                                                                          |
| qwen_large_nr      | qwen/qwen3.5-27b                     | non_reasoning | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,min_p,presence_penalty,reasoning,repetition_penalty,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_logprobs,top_p                                                                                                     |
| qwen_large_r       | SKIPPED                              | reasoning     | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,min_p,presence_penalty,reasoning,repetition_penalty,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_logprobs,top_p; probe_incompatible:qwen/qwen3.5-27b:multi_hop_035__natural_language:syntactic=False:semantic=False |
| glm_med_nr         | z-ai/glm-5                           | non_reasoning | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,min_p,presence_penalty,reasoning,repetition_penalty,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_logprobs,top_p                                                                                                     |
| glm_med_r          | SKIPPED                              | reasoning     | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,min_p,presence_penalty,reasoning,repetition_penalty,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_logprobs,top_p; probe_incompatible:z-ai/glm-5:extract_026__iso_8601:syntactic=False:semantic=False                 |

## Headline Format Comparison
| Format           | Accuracy | Strict | 95% CI           | Syntactic | Calendar | Compliance | Clean  |
| ---------------- | -------- | ------ | ---------------- | --------- | -------- | ---------- | ------ |
| iso_8601         | 88.10%   | 88.10% | 87.19% to 88.96% | 98.05%    | -        | 0.968      | 99.11% |
| javascript_date  | 78.12%   | 73.83% | 76.98% to 79.23% | 89.25%    | 79.94%   | 0.742      | 99.23% |
| natural_language | 76.31%   | 71.61% | 75.13% to 77.44% | 92.51%    | 82.26%   | 0.872      | 99.34% |
| python_datetime  | 87.64%   | 87.64% | 86.72% to 88.51% | 97.47%    | -        | 0.962      | 99.28% |
| rfc_2822         | 84.35%   | 80.35% | 83.34% to 85.32% | 95.44%    | 86.34%   | 0.934      | 98.76% |
| rfc_3339         | 88.24%   | 88.24% | 87.33% to 89.09% | 97.93%    | -        | 0.959      | 99.11% |
| unix_epoch       | 50.85%   | 50.85% | 49.49% to 52.21% | 86.60%    | -        | 0.737      | 96.60% |

## Primary Results
| task_type               | format           | anthropic_large_nr | anthropic_large_r | anthropic_med_nr | anthropic_med_r | anthropic_small_nr | anthropic_small_r | glm_med_nr | google_large_nr | google_large_r | google_med_nr | google_med_r | google_small_nr | google_small_r | openai_large_nr | openai_large_r | openai_med_nr | openai_med_nr_chat | openai_med_r | openai_small_nr | openai_small_r | qwen_large_nr | qwen_small_nr |
| ----------------------- | ---------------- | ------------------ | ----------------- | ---------------- | --------------- | ------------------ | ----------------- | ---------- | --------------- | -------------- | ------------- | ------------ | --------------- | -------------- | --------------- | -------------- | ------------- | ------------------ | ------------ | --------------- | -------------- | ------------- | ------------- |
| direct_generation       | iso_8601         | 100.0              | 100.0             | 100.0            | 100.0           | 97.14              | 100.0             | 100.0      | 100.0           | 100.0          | 100.0         | 100.0        | 100.0           | 100.0          | 100.0           | 100.0          | 97.14         | 100.0              | 100.0        | 100.0           | 100.0          | 100.0         | 97.14         |
| direct_generation       | javascript_date  | 100.0              | 100.0             | 100.0            | 100.0           | 91.43              | 97.14             | 97.14      | 100.0           | 97.14          | 100.0         | 100.0        | 100.0           | 100.0          | 100.0           | 85.71          | 91.43         | 100.0              | 100.0        | 100.0           | 100.0          | 14.29         | 0.0           |
| direct_generation       | natural_language | 100.0              | 100.0             | 97.14            | 100.0           | 94.29              | 94.29             | 91.43      | 100.0           | 100.0          | 82.86         | 97.14        | 97.14           | 82.86          | 97.14           | 82.86          | 94.29         | 94.29              | 85.71        | 97.14           | 94.29          | 51.43         | 48.57         |
| direct_generation       | python_datetime  | 100.0              | 100.0             | 100.0            | 100.0           | 97.14              | 100.0             | 100.0      | 100.0           | 100.0          | 100.0         | 100.0        | 100.0           | 100.0          | 100.0           | 100.0          | 100.0         | 100.0              | 100.0        | 97.14           | 100.0          | 94.29         | 91.43         |
| direct_generation       | rfc_2822         | 100.0              | 100.0             | 100.0            | 100.0           | 97.14              | 100.0             | 97.14      | 100.0           | 100.0          | 100.0         | 100.0        | 100.0           | 100.0          | 100.0           | 100.0          | 97.14         | 100.0              | 100.0        | 97.14           | 100.0          | 97.14         | 60.0          |
| direct_generation       | rfc_3339         | 100.0              | 100.0             | 100.0            | 100.0           | 97.14              | 100.0             | 100.0      | 100.0           | 100.0          | 100.0         | 100.0        | 100.0           | 100.0          | 100.0           | 100.0          | 100.0         | 100.0              | 100.0        | 100.0           | 100.0          | 100.0         | 100.0         |
| direct_generation       | unix_epoch       | 17.14              | 37.14             | 28.57            | 85.71           | 2.86               | 17.14             | 20.0       | 100.0           | 88.57          | 85.71         | 100.0        | 45.71           | 85.71          | 82.86           | 100.0          | 25.71         | 100.0              | 97.14        | 94.29           | 94.29          | 14.29         | 2.86          |
| edge_cases              | iso_8601         | 94.29              | 82.86             | 91.43            | 88.57           | 88.57              | 97.14             | 82.86      | 85.71           | 82.86          | 80.0          | 82.86        | 80.0            | 80.0           | 82.86           | 82.86          | 88.57         | 82.86              | 82.86        | 82.86           | 85.71          | 82.86         | 77.14         |
| edge_cases              | javascript_date  | 94.29              | 88.57             | 94.29            | 88.57           | 94.29              | 94.29             | 62.86      | 82.86           | 82.86          | 77.14         | 82.86        | 82.86           | 77.14          | 80.0            | 82.86          | 85.71         | 82.86              | 82.86        | 85.71           | 85.71          | 5.71          | 0.0           |
| edge_cases              | natural_language | 82.86              | 85.71             | 80.0             | 88.57           | 88.57              | 94.29             | 80.0       | 82.86           | 85.71          | 71.43         | 82.86        | 88.57           | 62.86          | 88.57           | 80.0           | 97.14         | 85.71              | 85.71        | 88.57           | 88.57          | 31.43         | 37.14         |
| edge_cases              | python_datetime  | 82.86              | 88.57             | 97.14            | 91.43           | 88.57              | 94.29             | 82.86      | 82.86           | 85.71          | 80.0          | 82.86        | 80.0            | 80.0           | 85.71           | 82.86          | 91.43         | 82.86              | 100.0        | 85.71           | 85.71          | 80.0          | 74.29         |
| edge_cases              | rfc_2822         | 94.29              | 82.86             | 80.0             | 88.57           | 88.57              | 91.43             | 80.0       | 82.86           | 85.71          | 74.29         | 82.86        | 77.14           | 74.29          | 82.86           | 82.86          | 91.43         | 82.86              | 85.71        | 85.71           | 88.57          | 65.71         | 45.71         |
| edge_cases              | rfc_3339         | 94.29              | 82.86             | 94.29            | 88.57           | 88.57              | 91.43             | 82.86      | 82.86           | 85.71          | 80.0          | 82.86        | 80.0            | 80.0           | 82.86           | 82.86          | 82.86         | 82.86              | 85.71        | 85.71           | 88.57          | 82.86         | 71.43         |
| edge_cases              | unix_epoch       | 14.29              | 60.0              | 20.0             | 85.71           | 0.0                | 31.43             | 25.71      | 85.71           | 77.14          | 60.0          | 77.14        | 11.43           | 48.57          | 51.43           | 80.0           | 8.57          | 80.0               | 80.0         | 68.57           | 82.86          | 11.43         | 8.57          |
| extraction_from_passage | iso_8601         | 73.33              | 80.0              | 86.67            | 93.33           | 70.0               | 63.33             | 83.33      | 80.0            | 76.67          | 86.67         | 73.33        | 70.0            | 80.0           | 86.67           | 90.0           | 86.67         | 96.67              | 93.33        | 83.33           | 83.33          | 43.33         | 46.67         |
| extraction_from_passage | javascript_date  | 70.0               | 90.0              | 73.33            | 80.0            | 56.67              | 80.0              | 46.67      | 80.0            | 76.67          | 83.33         | 70.0         | 73.33           | 83.33          | 70.0            | 80.0           | 53.33         | 96.67              | 96.67        | 90.0            | 86.67          | 0.0           | 0.0           |
| extraction_from_passage | natural_language | 76.67              | 70.0              | 80.0             | 76.67           | 86.67              | 76.67             | 50.0       | 80.0            | 76.67          | 83.33         | 70.0         | 70.0            | 80.0           | 86.67           | 100.0          | 66.67         | 83.33              | 76.67        | 70.0            | 73.33          | 3.33          | 16.67         |
| extraction_from_passage | python_datetime  | 66.67              | 83.33             | 80.0             | 86.67           | 86.67              | 70.0              | 96.67      | 76.67           | 76.67          | 86.67         | 63.33        | 70.0            | 83.33          | 90.0            | 93.33          | 66.67         | 96.67              | 96.67        | 80.0            | 86.67          | 60.0          | 40.0          |
| extraction_from_passage | rfc_2822         | 80.0               | 86.67             | 83.33            | 83.33           | 80.0               | 60.0              | 90.0       | 80.0            | 73.33          | 86.67         | 73.33        | 70.0            | 83.33          | 90.0            | 96.67          | 80.0          | 96.67              | 93.33        | 83.33           | 90.0           | 13.33         | 26.67         |
| extraction_from_passage | rfc_3339         | 66.67              | 76.67             | 83.33            | 96.67           | 76.67              | 70.0              | 86.67      | 80.0            | 76.67          | 93.33         | 80.0         | 70.0            | 86.67          | 96.67           | 93.33          | 83.33         | 100.0              | 90.0         | 76.67           | 80.0           | 43.33         | 43.33         |
| extraction_from_passage | unix_epoch       | 10.0               | 53.33             | 13.33            | 73.33           | 0.0                | 23.33             | 10.0       | 83.33           | 80.0           | 53.33         | 63.33        | 20.0            | 56.67          | 50.0            | 96.67          | 13.33         | 93.33              | 90.0         | 63.33           | 76.67          | 3.33          | 0.0           |
| format_conversion       | iso_8601         | 85.71              | 100.0             | 88.57            | 91.43           | 85.71              | 85.71             | 88.57      | 100.0           | 94.29          | 94.29         | 94.29        | 97.14           | 94.29          | 85.71           | 100.0          | 85.71         | 97.14              | 100.0        | 100.0           | 97.14          | 88.57         | 85.71         |
| format_conversion       | javascript_date  | 91.43              | 94.29             | 91.43            | 91.43           | 85.71              | 88.57             | 62.86      | 94.29           | 94.29          | 94.29         | 97.14        | 91.43           | 94.29          | 85.71           | 94.29          | 82.86         | 97.14              | 100.0        | 100.0           | 97.14          | 2.86          | 0.0           |
| format_conversion       | natural_language | 77.14              | 85.71             | 65.71            | 77.14           | 74.29              | 74.29             | 57.14      | 97.14           | 91.43          | 68.57         | 65.71        | 68.57           | 71.43          | 42.86           | 40.0           | 68.57         | 60.0               | 37.14        | 80.0            | 85.71          | 2.86          | 11.43         |
| format_conversion       | python_datetime  | 82.86              | 97.14             | 82.86            | 88.57           | 80.0               | 85.71             | 80.0       | 100.0           | 97.14          | 94.29         | 94.29        | 88.57           | 88.57          | 80.0            | 100.0          | 80.0          | 94.29              | 100.0        | 94.29           | 91.43          | 80.0          | 77.14         |
| format_conversion       | rfc_2822         | 85.71              | 91.43             | 82.86            | 91.43           | 85.71              | 85.71             | 82.86      | 100.0           | 100.0          | 94.29         | 91.43        | 94.29           | 94.29          | 82.86           | 100.0          | 82.86         | 91.43              | 100.0        | 94.29           | 97.14          | 74.29         | 57.14         |
| format_conversion       | rfc_3339         | 88.57              | 94.29             | 88.57            | 88.57           | 88.57              | 88.57             | 91.43      | 100.0           | 97.14          | 94.29         | 91.43        | 88.57           | 91.43          | 88.57           | 100.0          | 88.57         | 97.14              | 100.0        | 97.14           | 97.14          | 88.57         | 88.57         |
| format_conversion       | unix_epoch       | 25.71              | 45.71             | 20.0             | 77.14           | 0.0                | 34.29             | 8.57       | 97.14           | 94.29          | 77.14         | 100.0        | 31.43           | 71.43          | 68.57           | 88.57          | 11.43         | 100.0              | 97.14        | 100.0           | 97.14          | 11.43         | 0.0           |
| multi_hop_reasoning     | iso_8601         | 97.14              | 100.0             | 77.14            | 100.0           | 25.71              | 80.0              | 94.29      | 97.14           | 91.43          | 91.43         | 100.0        | 91.43           | 94.29          | 82.86           | 100.0          | 40.0          | 97.14              | 100.0        | 100.0           | 97.14          | 77.14         | 62.86         |
| multi_hop_reasoning     | javascript_date  | 85.71              | 97.14             | 51.43            | 94.29           | 14.29              | 77.14             | 60.0       | 100.0           | 88.57          | 77.14         | 100.0        | 82.86           | 74.29          | 65.71           | 100.0          | 54.29         | 94.29              | 97.14        | 100.0           | 97.14          | 0.0           | 0.0           |

Truncated in summary; full table is in `primary_results.csv`.

## Pairwise Format Tests
| Left             | Right            | Test        | p-value      |
| ---------------- | ---------------- | ----------- | ------------ |
| iso_8601         | javascript_date  | chi_squared | 8.44126e-42  |
| iso_8601         | natural_language | chi_squared | 1.92962e-55  |
| iso_8601         | python_datetime  | chi_squared | 0.469682     |
| iso_8601         | rfc_2822         | chi_squared | 3.08875e-08  |
| iso_8601         | rfc_3339         | chi_squared | 0.831197     |
| iso_8601         | unix_epoch       | chi_squared | 0            |
| javascript_date  | natural_language | chi_squared | 0.027532     |
| javascript_date  | python_datetime  | chi_squared | 9.12546e-38  |
| javascript_date  | rfc_2822         | chi_squared | 5.01954e-16  |
| javascript_date  | rfc_3339         | chi_squared | 5.01555e-43  |
| javascript_date  | unix_epoch       | chi_squared | 1.34146e-184 |
| natural_language | python_datetime  | chi_squared | 8.36917e-51  |
| natural_language | rfc_2822         | chi_squared | 7.69019e-25  |
| natural_language | rfc_3339         | chi_squared | 7.64353e-57  |
| natural_language | unix_epoch       | chi_squared | 2.55678e-159 |
| python_datetime  | rfc_2822         | chi_squared | 1.4534e-06   |
| python_datetime  | rfc_3339         | chi_squared | 0.349207     |
| python_datetime  | unix_epoch       | chi_squared | 0            |
| rfc_2822         | rfc_3339         | chi_squared | 9.03109e-09  |
| rfc_2822         | unix_epoch       | chi_squared | 5.02325e-290 |
| rfc_3339         | unix_epoch       | chi_squared | 0            |

## Interaction Highlights
| Mode          | Format           | Accuracy | Strict | Correct | N    |
| ------------- | ---------------- | -------- | ------ | ------- | ---- |
| non_reasoning | iso_8601         | 86.25%   | 86.25% | 2635    | 3055 |
| non_reasoning | javascript_date  | 70.28%   | 65.24% | 2147    | 3055 |
| non_reasoning | natural_language | 71.59%   | 65.56% | 2187    | 3055 |
| non_reasoning | python_datetime  | 85.20%   | 85.20% | 2603    | 3055 |
| non_reasoning | rfc_2822         | 80.39%   | 75.06% | 2456    | 3055 |
| non_reasoning | rfc_3339         | 86.22%   | 86.22% | 2634    | 3055 |
| non_reasoning | unix_epoch       | 36.40%   | 36.40% | 1112    | 3055 |
| reasoning     | iso_8601         | 90.78%   | 90.78% | 1920    | 2115 |
| reasoning     | javascript_date  | 89.46%   | 86.24% | 1892    | 2115 |
| reasoning     | natural_language | 83.12%   | 80.33% | 1758    | 2115 |
| reasoning     | python_datetime  | 91.16%   | 91.16% | 1928    | 2115 |
| reasoning     | rfc_2822         | 90.07%   | 87.99% | 1905    | 2115 |
| reasoning     | rfc_3339         | 91.16%   | 91.16% | 1928    | 2115 |
| reasoning     | unix_epoch       | 71.73%   | 71.73% | 1517    | 2115 |

| Size   | Format           | Accuracy | Strict | Correct | N    |
| ------ | ---------------- | -------- | ------ | ------- | ---- |
| large  | iso_8601         | 89.24%   | 89.24% | 1468    | 1645 |
| large  | javascript_date  | 76.35%   | 74.47% | 1256    | 1645 |
| large  | natural_language | 76.53%   | 74.41% | 1259    | 1645 |
| large  | python_datetime  | 88.94%   | 88.94% | 1463    | 1645 |
| large  | rfc_2822         | 86.69%   | 85.29% | 1426    | 1645 |
| large  | rfc_3339         | 89.36%   | 89.36% | 1470    | 1645 |
| large  | unix_epoch       | 55.74%   | 55.74% | 917     | 1645 |
| medium | iso_8601         | 89.57%   | 89.57% | 1684    | 1880 |
| medium | javascript_date  | 84.57%   | 81.12% | 1590    | 1880 |
| medium | natural_language | 79.68%   | 75.74% | 1498    | 1880 |
| medium | python_datetime  | 89.52%   | 89.52% | 1683    | 1880 |
| medium | rfc_2822         | 87.23%   | 83.51% | 1640    | 1880 |
| medium | rfc_3339         | 89.95%   | 89.95% | 1691    | 1880 |
| medium | unix_epoch       | 56.91%   | 56.91% | 1070    | 1880 |
| small  | iso_8601         | 85.29%   | 85.29% | 1403    | 1645 |
| small  | javascript_date  | 72.52%   | 64.86% | 1193    | 1645 |
| small  | natural_language | 72.22%   | 64.07% | 1188    | 1645 |
| small  | python_datetime  | 84.19%   | 84.19% | 1385    | 1645 |
| small  | rfc_2822         | 78.72%   | 71.79% | 1295    | 1645 |
| small  | rfc_3339         | 85.17%   | 85.17% | 1401    | 1645 |
| small  | unix_epoch       | 39.03%   | 39.03% | 642     | 1645 |

| Task Type               | Best Format     | Best Accuracy | Worst Format | Worst Accuracy | Spread |
| ----------------------- | --------------- | ------------- | ------------ | -------------- | ------ |
| multi_hop_reasoning     | python_datetime | 86.36%        | unix_epoch   | 45.06%         | 41.30% |
| direct_generation       | rfc_3339        | 99.87%        | unix_epoch   | 60.26%         | 39.61% |
| temporal_arithmetic     | rfc_3339        | 79.09%        | unix_epoch   | 40.57%         | 38.52% |
| parsing_normalization   | iso_8601        | 99.09%        | unix_epoch   | 61.64%         | 37.45% |
| edge_cases              | python_datetime | 85.71%        | unix_epoch   | 48.57%         | 37.14% |
| format_conversion       | iso_8601        | 92.73%        | unix_epoch   | 57.14%         | 35.58% |
| extraction_from_passage | rfc_3339        | 79.55%        | unix_epoch   | 46.67%         | 32.88% |

## Error Taxonomy
| Format   | Model Cell         | Error Type       | Count |
| -------- | ------------------ | ---------------- | ----- |
| iso_8601 | anthropic_large_nr | arithmetic_error | 7     |
| iso_8601 | anthropic_large_nr | extraction_error | 8     |
| iso_8601 | anthropic_large_nr | timezone_error   | 2     |
| iso_8601 | anthropic_large_nr | unknown          | 5     |
| iso_8601 | anthropic_large_r  | arithmetic_error | 11    |
| iso_8601 | anthropic_large_r  | extraction_error | 6     |
| iso_8601 | anthropic_large_r  | timezone_error   | 3     |
| iso_8601 | anthropic_med_nr   | arithmetic_error | 16    |
| iso_8601 | anthropic_med_nr   | extraction_error | 4     |
| iso_8601 | anthropic_med_nr   | timezone_error   | 3     |
| iso_8601 | anthropic_med_nr   | unknown          | 4     |
| iso_8601 | anthropic_med_r    | arithmetic_error | 9     |
| iso_8601 | anthropic_med_r    | extraction_error | 2     |
| iso_8601 | anthropic_med_r    | timezone_error   | 2     |
| iso_8601 | anthropic_med_r    | unknown          | 3     |
| iso_8601 | anthropic_small_nr | arithmetic_error | 42    |
| iso_8601 | anthropic_small_nr | extraction_error | 9     |
| iso_8601 | anthropic_small_nr | timezone_error   | 8     |
| iso_8601 | anthropic_small_nr | unknown          | 5     |
| iso_8601 | anthropic_small_r  | arithmetic_error | 13    |
| iso_8601 | anthropic_small_r  | extraction_error | 11    |
| iso_8601 | anthropic_small_r  | timezone_error   | 3     |
| iso_8601 | anthropic_small_r  | unknown          | 5     |
| iso_8601 | glm_med_nr         | arithmetic_error | 10    |
| iso_8601 | glm_med_nr         | extraction_error | 2     |
| iso_8601 | glm_med_nr         | syntax_error     | 10    |
| iso_8601 | glm_med_nr         | timezone_error   | 3     |
| iso_8601 | google_large_nr    | arithmetic_error | 9     |
| iso_8601 | google_large_nr    | extraction_error | 6     |
| iso_8601 | google_large_nr    | syntax_error     | 1     |

Truncated in summary; full table is in `error_taxonomy.csv`.

## Cost Report
| Category         | Name                    | Cost USD   | Reason                                                                                                                                                                                                                                                                                                                                             |
| ---------------- | ----------------------- | ---------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| total            | all                     | 120.640371 |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | anthropic_large_nr      | 3.38061    |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | anthropic_large_r       | 11.854047  |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | anthropic_med_nr        | 2.120926   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | anthropic_med_r         | 7.206638   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | anthropic_small_nr      | 0.446032   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | anthropic_small_r       | 5.597237   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | glm_med_nr              | 6.011525   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | google_large_nr         | 22.790236  |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | google_large_r          | 15.148572  |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | google_med_nr           | 0.2508     |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | google_med_r            | 5.413735   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | google_small_nr         | 0.126428   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | google_small_r          | 0.251657   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | openai_large_nr         | 1.127238   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | openai_large_r          | 12.744914  |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | openai_med_nr           | 0.737481   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | openai_med_nr_chat      | 7.615169   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | openai_med_r            | 5.808449   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | openai_small_nr         | 2.644991   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | openai_small_r          | 1.522137   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | qwen_large_nr           | 7.346555   |                                                                                                                                                                                                                                                                                                                                                    |
| model_cell       | qwen_small_nr           | 0.494995   |                                                                                                                                                                                                                                                                                                                                                    |
| task_type        | direct_generation       | 12.974704  |                                                                                                                                                                                                                                                                                                                                                    |
| task_type        | edge_cases              | 17.272507  |                                                                                                                                                                                                                                                                                                                                                    |
| task_type        | extraction_from_passage | 18.432046  |                                                                                                                                                                                                                                                                                                                                                    |
| task_type        | format_conversion       | 16.668027  |                                                                                                                                                                                                                                                                                                                                                    |
| task_type        | multi_hop_reasoning     | 21.689165  |                                                                                                                                                                                                                                                                                                                                                    |
| task_type        | parsing_normalization   | 9.861772   |                                                                                                                                                                                                                                                                                                                                                    |
| task_type        | temporal_arithmetic     | 23.742151  |                                                                                                                                                                                                                                                                                                                                                    |
| unavailable_cell | qwen_large_r            | 0.0        | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,min_p,presence_penalty,reasoning,repetition_penalty,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_logprobs,top_p;probe_incompatible:qwen/qwen3.5-27b:multi_hop_035__natural_language:syntactic=False:semantic=False |
| unavailable_cell | glm_med_r               | 0.0        | supported_parameters=frequency_penalty,include_reasoning,logit_bias,logprobs,max_tokens,min_p,presence_penalty,reasoning,repetition_penalty,response_format,seed,stop,structured_outputs,temperature,tool_choice,tools,top_k,top_logprobs,top_p;probe_incompatible:z-ai/glm-5:extract_026__iso_8601:syntactic=False:semantic=False                 |

## Recommendations
- Highest string-format reliability: `rfc_3339` at 88.24% with 95% CI 87.33% to 89.09%.
- `rfc_3339` vs `iso_8601`: chi_squared p-value = 0.831197.
- `rfc_3339` vs `javascript_date`: chi_squared p-value = 5.01555e-43.
- `rfc_3339` vs `natural_language`: chi_squared p-value = 7.64353e-57.
- `rfc_3339` vs `python_datetime`: chi_squared p-value = 0.349207.
- `rfc_3339` vs `rfc_2822`: chi_squared p-value = 9.03109e-09.
- `rfc_3339` vs `unix_epoch`: chi_squared p-value = 0.
- Size `large` ranking: rfc_3339 89.36%, iso_8601 89.24%, python_datetime 88.94%, rfc_2822 86.69%, natural_language 76.53%, javascript_date 76.35%, unix_epoch 55.74%.
- Size `medium` ranking: rfc_3339 89.95%, iso_8601 89.57%, python_datetime 89.52%, rfc_2822 87.23%, javascript_date 84.57%, natural_language 79.68%, unix_epoch 56.91%.
- Size `small` ranking: iso_8601 85.29%, rfc_3339 85.17%, python_datetime 84.19%, rfc_2822 78.72%, javascript_date 72.52%, natural_language 72.22%, unix_epoch 39.03%.
- Reasoning delta for `iso_8601`: 90.78% vs 86.25% (`+4.53` points).
- Reasoning delta for `javascript_date`: 89.46% vs 70.28% (`+19.18` points).
- Reasoning delta for `natural_language`: 83.12% vs 71.59% (`+11.53` points).
- Reasoning delta for `python_datetime`: 91.16% vs 85.20% (`+5.95` points).
- Reasoning delta for `rfc_2822`: 90.07% vs 80.39% (`+9.68` points).
- Reasoning delta for `rfc_3339`: 91.16% vs 86.22% (`+4.94` points).
- Reasoning delta for `unix_epoch`: 71.73% vs 36.40% (`+35.33` points).
- Most format-sensitive tasks: `multi_hop_reasoning` (python_datetime 86.36% vs unix_epoch 45.06%); `direct_generation` (rfc_3339 99.87% vs unix_epoch 60.26%); `temporal_arithmetic` (rfc_3339 79.09% vs unix_epoch 40.57%).
- System-prompt recommendation: Use `RFC 3339` as the default machine-facing timestamp format. It is statistically tied with the top cluster and names an unambiguous spec.
- Main recommendation surface: string formats only. `unix_epoch` is reported separately.
- `unix_epoch` is analyzed separately from string formats for default-format recommendations.
- Reasoning vs non-reasoning summaries reflect the configured production request shapes (temperature 1.0 vs 0.0), not an isolated causal reasoning estimate.
- Common `iso_8601` error modes: arithmetic_error (283), extraction_error (106), syntax_error (100).
- Common `javascript_date` error modes: syntax_error (551), arithmetic_error (205), day_of_week_error (189).
- Common `natural_language` error modes: syntax_error (387), timezone_error (289), day_of_week_error (213).
- Common `python_datetime` error modes: arithmetic_error (261), syntax_error (130), extraction_error (108).
- Common `rfc_2822` error modes: syntax_error (235), arithmetic_error (204), day_of_week_error (192).
- Common `rfc_3339` error modes: arithmetic_error (283), syntax_error (106), extraction_error (100).
- Common `unix_epoch` error modes: epoch_conversion_error (1583), syntax_error (691), extraction_error (265).
- Total benchmark spend: $120.640371.
