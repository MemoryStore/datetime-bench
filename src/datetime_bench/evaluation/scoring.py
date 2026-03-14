# AI-ANCHOR: datetime-bench eval: metric computation and error taxonomy
"""Metric computation for benchmark responses."""

from __future__ import annotations

from datetime import UTC

from ..config import SEMANTIC_THRESHOLDS_SECONDS
from ..types import EvaluationResult, ParseResult, PromptCase
from .parsers import (
    extract_weekday,
    has_weekday_token,
    parse_iso_8601,
    parse_javascript_date,
    parse_natural_language,
    parse_python_datetime,
    parse_rfc_2822,
    parse_rfc_3339,
    parse_unix_epoch,
)


def evaluate_case(case: PromptCase, raw_output: str, parse_result: ParseResult) -> EvaluationResult:
    extraction_clean = (raw_output or "").strip() == parse_result.cleaned_output
    if case.task_type == "multiple_choice_validation":
        return _evaluate_multiple_choice(case, extraction_clean, parse_result)

    semantic_correct = False
    strict_correct = False
    delta_seconds = None
    calendar_consistent = None
    if parse_result.parsed_datetime is not None:
        parsed_utc = parse_result.parsed_datetime.astimezone(UTC)
        gold_utc = case.gold_datetime.astimezone(UTC)
        delta_seconds = abs((parsed_utc - gold_utc).total_seconds())
        semantic_correct = delta_seconds <= semantic_threshold_seconds(case.task_type)
        strict_correct = delta_seconds == 0 and parse_result.parse_mode == "strict"
    if case.format_key in {"rfc_2822", "natural_language", "javascript_date"}:
        calendar_consistent = _calendar_consistent(case, parse_result.cleaned_output)
        if calendar_consistent is False:
            strict_correct = False

    compliance = normalized_compliance(parse_result.cleaned_output, case.gold_formatted)
    error_type, error_subtype = classify_error(
        case,
        parse_result,
        semantic_correct=semantic_correct,
        extraction_clean=extraction_clean,
        calendar_consistent=calendar_consistent,
    )
    return EvaluationResult(
        syntactic_valid=parse_result.syntactic_valid,
        semantic_correct=semantic_correct,
        strict_correct=strict_correct,
        calendar_consistent=calendar_consistent,
        format_compliance=compliance,
        extraction_clean=extraction_clean,
        error_type=error_type,
        error_subtype=error_subtype,
        delta_seconds=delta_seconds,
        parse_mode=parse_result.parse_mode,
        warnings=list(parse_result.warnings),
    )


def _evaluate_multiple_choice(
    case: PromptCase,
    extraction_clean: bool,
    parse_result: ParseResult,
) -> EvaluationResult:
    gold_choice = str(case.metadata.get("correct_choice") or "")
    semantic_correct = parse_result.selected_choice == gold_choice and parse_result.syntactic_valid
    error_type = None
    error_subtype = None
    if not semantic_correct:
        if not parse_result.syntactic_valid and parse_result.selected_option_content is not None:
            error_type = "instruction_violation"
            error_subtype = "returned_option_content"
        elif not parse_result.syntactic_valid:
            error_type = "syntax_error"
        else:
            error_type = "unknown"
            error_subtype = "wrong_choice"
    return EvaluationResult(
        syntactic_valid=parse_result.syntactic_valid,
        semantic_correct=semantic_correct,
        strict_correct=semantic_correct,
        calendar_consistent=None,
        format_compliance=normalized_compliance(parse_result.cleaned_output, gold_choice),
        extraction_clean=extraction_clean,
        error_type=error_type,
        error_subtype=error_subtype,
        delta_seconds=None,
        parse_mode=parse_result.parse_mode,
        warnings=list(parse_result.warnings),
        selected_choice=parse_result.selected_choice,
        selected_option_content=parse_result.selected_option_content,
    )


def _calendar_consistent(case: PromptCase, cleaned_output: str) -> bool:
    observed = extract_weekday(cleaned_output, case.format_key)
    if observed is None:
        return False
    expected = case.gold_datetime.strftime("%a") if case.format_key in {"rfc_2822", "javascript_date"} else case.gold_datetime.strftime("%A")
    return observed == expected


def classify_error(
    case: PromptCase,
    parse_result: ParseResult,
    *,
    semantic_correct: bool,
    extraction_clean: bool,
    calendar_consistent: bool | None,
) -> tuple[str | None, str | None]:
    if semantic_correct:
        return None, None
    if not parse_result.syntactic_valid:
        if not extraction_clean:
            return "instruction_violation", None
        if case.format_key in {"iso_8601", "rfc_3339", "python_datetime"} and has_weekday_token(parse_result.cleaned_output):
            return "format_error", "format_contamination"
        if _parses_as_other_format(case.format_key, parse_result.cleaned_output):
            return "format_error", None
        return "syntax_error", None
    if case.task_type == "extraction_from_passage":
        return "extraction_error", None
    if case.format_key == "unix_epoch":
        return "epoch_conversion_error", None
    if calendar_consistent is False:
        return "day_of_week_error", None
    if _is_timezone_error(case, parse_result):
        return "timezone_error", None
    if case.task_type in {"temporal_arithmetic", "multi_hop_reasoning", "edge_cases"}:
        return "arithmetic_error", None
    return "unknown", None


def _is_timezone_error(case: PromptCase, parse_result: ParseResult) -> bool:
    parsed = parse_result.parsed_datetime
    gold = case.gold_datetime
    if parsed is None:
        return False
    same_local = (
        parsed.year,
        parsed.month,
        parsed.day,
        parsed.hour,
        parsed.minute,
    ) == (
        gold.year,
        gold.month,
        gold.day,
        gold.hour,
        gold.minute,
    )
    return same_local and parsed.utcoffset() != gold.utcoffset()


def _parses_as_other_format(target_format: str, cleaned_output: str) -> bool:
    parsers = {
        "iso_8601": parse_iso_8601,
        "rfc_3339": parse_rfc_3339,
        "rfc_2822": parse_rfc_2822,
        "natural_language": parse_natural_language,
        "javascript_date": parse_javascript_date,
        "python_datetime": parse_python_datetime,
        "unix_epoch": parse_unix_epoch,
    }
    for format_key, parser in parsers.items():
        if format_key == target_format:
            continue
        if parser(cleaned_output).syntactic_valid:
            return True
    return False


def semantic_threshold_seconds(task_type: str) -> float:
    return float(SEMANTIC_THRESHOLDS_SECONDS.get(task_type, SEMANTIC_THRESHOLDS_SECONDS["default"]))


def normalized_compliance(observed: str, expected: str) -> float:
    if not expected:
        return 0.0
    distance = levenshtein_distance(observed, expected)
    return max(0.0, 1.0 - (distance / max(len(expected), 1)))


def levenshtein_distance(left: str, right: str) -> int:
    if left == right:
        return 0
    if not left:
        return len(right)
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for i, left_char in enumerate(left, start=1):
        current = [i]
        for j, right_char in enumerate(right, start=1):
            insertions = previous[j] + 1
            deletions = current[j - 1] + 1
            substitutions = previous[j - 1] + (left_char != right_char)
            current.append(min(insertions, deletions, substitutions))
        previous = current
    return previous[-1]
