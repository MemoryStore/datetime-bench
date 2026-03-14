# AI-ANCHOR: datetime-bench eval: parsing and output cleanup
"""Format-specific cleanup and parsing helpers."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

from dateutil import parser as dateutil_parser
from dateutil.parser import ParserError
from dateutil.tz import tzoffset

from ..types import ParseResult, PromptCase

PREFIX_RE = re.compile(
    r"^(?:answer|final answer|here(?: is)?(?: the datetime)?|datetime|output)\s*[:\-]\s*",
    re.IGNORECASE,
)
ISO_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}(?::\d{2}(?:\.\d{1,6})?)?(?:Z|[+-]\d{2}:\d{2})$"
)
RFC3339_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?(?:Z|[+-]\d{2}:\d{2})$"
)
PYTHON_DATETIME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(?:\.\d{1,6})?[+-]\d{2}:\d{2}$"
)
UNIX_EPOCH_RE = re.compile(r"^-?\d{10}(?:\d{3})?$")
JAVASCRIPT_DATE_RE = re.compile(
    r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun) "
    r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) "
    r"\d{2} \d{4} \d{2}:\d{2}:\d{2} GMT[+-]\d{4}(?: \(.+\))?$"
)
IANA_TZ_RE = re.compile(r"(?:in timezone\s+)?([A-Za-z_]+/[A-Za-z_]+(?:/[A-Za-z_]+)?)$")
DAY_ABBR_RE = re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun),", re.IGNORECASE)
DAY_ABBR_SPACE_RE = re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\b", re.IGNORECASE)
DAY_FULL_RE = re.compile(
    r"\b(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b",
    re.IGNORECASE,
)

TZINFOS = {
    "UTC": tzoffset("UTC", 0),
    "GMT": tzoffset("GMT", 0),
    "BST": tzoffset("BST", 3600),
    "EST": tzoffset("EST", -18000),
    "EDT": tzoffset("EDT", -14400),
    "PST": tzoffset("PST", -28800),
    "PDT": tzoffset("PDT", -25200),
    "CST": tzoffset("CST", -21600),
    "CDT": tzoffset("CDT", -18000),
    "JST": tzoffset("JST", 32400),
    "CET": tzoffset("CET", 3600),
    "CEST": tzoffset("CEST", 7200),
    "ACDT": tzoffset("ACDT", 37800),
    "ACST": tzoffset("ACST", 34200),
    "AEDT": tzoffset("AEDT", 39600),
    "AEST": tzoffset("AEST", 36000),
    "LHDT": tzoffset("LHDT", 39600),
    "LHST": tzoffset("LHST", 37800),
    "NZDT": tzoffset("NZDT", 46800),
    "NZST": tzoffset("NZST", 43200),
    "IST": tzoffset("IST", 19800),
    "Pacific Daylight Time": tzoffset("PDT", -25200),
    "Pacific Standard Time": tzoffset("PST", -28800),
    "Central Daylight Time": tzoffset("CDT", -18000),
    "Central Standard Time": tzoffset("CST", -21600),
    "Eastern Daylight Time": tzoffset("EDT", -14400),
    "Eastern Standard Time": tzoffset("EST", -18000),
    "British Summer Time": tzoffset("BST", 3600),
    "Greenwich Mean Time": tzoffset("GMT", 0),
    "Central European Standard Time": tzoffset("CET", 3600),
    "Central European Summer Time": tzoffset("CEST", 7200),
    "Australian Central Daylight Time": tzoffset("ACDT", 37800),
    "Australian Central Standard Time": tzoffset("ACST", 34200),
    "Japan Standard Time": tzoffset("JST", 32400),
    "Australian Eastern Daylight Time": tzoffset("AEDT", 39600),
    "Australian Eastern Standard Time": tzoffset("AEST", 36000),
    "Lord Howe Daylight Time": tzoffset("LHDT", 39600),
    "Lord Howe Standard Time": tzoffset("LHST", 37800),
    "New Zealand Daylight Time": tzoffset("NZDT", 46800),
    "New Zealand Standard Time": tzoffset("NZST", 43200),
    "India Standard Time": tzoffset("IST", 19800),
}

QUOTE_CHARS = "`'\"“”‘’"


def clean_output(raw_output: str) -> str:
    stripped = (raw_output or "").strip()
    if not stripped:
        return ""
    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    candidate = lines[-1] if lines else stripped
    candidate = candidate.strip(QUOTE_CHARS + " ")
    prior = None
    while candidate != prior:
        prior = candidate
        candidate = PREFIX_RE.sub("", candidate).strip()
        candidate = candidate.strip(QUOTE_CHARS + " ")
        if candidate.startswith("```") and candidate.endswith("```"):
            candidate = candidate[3:-3].strip()
    if len(candidate) >= 2 and candidate[0] in "ABCDabcd" and candidate[1] in ").":
        candidate = candidate[0]
    return candidate.strip()


def parse_output(case: PromptCase, cleaned_output: str) -> ParseResult:
    if case.task_type == "multiple_choice_validation":
        return parse_multiple_choice(cleaned_output, case)
    if case.format_key == "iso_8601":
        return parse_iso_8601(cleaned_output)
    if case.format_key == "rfc_3339":
        return parse_rfc_3339(cleaned_output)
    if case.format_key == "rfc_2822":
        return parse_rfc_2822(cleaned_output)
    if case.format_key == "javascript_date":
        return parse_javascript_date(cleaned_output)
    if case.format_key == "python_datetime":
        return parse_python_datetime(cleaned_output)
    if case.format_key == "unix_epoch":
        return parse_unix_epoch(cleaned_output)
    return parse_natural_language(cleaned_output)


def parse_iso_8601(cleaned_output: str) -> ParseResult:
    warnings: list[str] = []
    candidate = cleaned_output.strip()
    if not ISO_RE.match(candidate):
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    if " " in candidate:
        warnings.append("space_separator")
    normalized = candidate[:-1] + "+00:00" if candidate.endswith("Z") else candidate
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    if parsed.tzinfo is None:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    return ParseResult(
        cleaned_output=candidate,
        syntactic_valid=True,
        parsed_datetime=parsed,
        parse_mode="strict",
        warnings=warnings,
    )


def parse_rfc_3339(cleaned_output: str) -> ParseResult:
    candidate = cleaned_output.strip()
    if not RFC3339_RE.match(candidate):
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    normalized = candidate[:-1] + "+00:00" if candidate.endswith("Z") else candidate
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    if parsed.tzinfo is None:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    return ParseResult(
        cleaned_output=candidate,
        syntactic_valid=True,
        parsed_datetime=parsed,
        parse_mode="strict",
    )


def parse_rfc_2822(cleaned_output: str) -> ParseResult:
    warnings: list[str] = []
    candidate = cleaned_output.strip()
    parsed = None
    try:
        parsed = parsedate_to_datetime(candidate)
    except (TypeError, ValueError):
        parsed = None
    if parsed is not None and parsed.tzinfo is not None:
        if re.search(r" [A-Z]{2,5}$", candidate):
            warnings.append("named_timezone")
        return ParseResult(
            cleaned_output=candidate,
            syntactic_valid=True,
            parsed_datetime=parsed,
            parse_mode="strict",
            warnings=warnings,
        )
    try:
        parsed = dateutil_parser.parse(candidate, fuzzy=False, tzinfos=TZINFOS)
    except (ParserError, ValueError, OverflowError):
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    if parsed.tzinfo is None:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    warnings.append("loose_parse")
    return ParseResult(
        cleaned_output=candidate,
        syntactic_valid=True,
        parsed_datetime=parsed,
        parse_mode="loose",
        warnings=warnings,
    )


def parse_natural_language(cleaned_output: str) -> ParseResult:
    warnings: list[str] = []
    candidate = cleaned_output.strip()
    working = candidate
    tzinfo = None

    match = IANA_TZ_RE.search(working)
    if match:
        try:
            tzinfo = ZoneInfo(match.group(1))
            working = working[: match.start()].rstrip(" ,")
            warnings.append("iana_timezone")
        except Exception:
            tzinfo = None

    if tzinfo is None:
        for name, mapped in sorted(TZINFOS.items(), key=lambda item: len(item[0]), reverse=True):
            token = f" {name}"
            if working.endswith(token):
                tzinfo = mapped
                working = working[: -len(token)].rstrip(" ,")
                break

    try:
        parsed = dateutil_parser.parse(working, fuzzy=False, tzinfos=TZINFOS)
        parse_mode = "strict"
    except (ParserError, ValueError, OverflowError):
        try:
            parsed = dateutil_parser.parse(working, fuzzy=True, tzinfos=TZINFOS)
            parse_mode = "fuzzy"
            warnings.append("fuzzy_parse")
        except (ParserError, ValueError, OverflowError):
            return ParseResult(cleaned_output=candidate, syntactic_valid=False)

    if parsed.tzinfo is None and tzinfo is not None:
        parsed = parsed.replace(tzinfo=tzinfo)
    if parsed.tzinfo is None:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    return ParseResult(
        cleaned_output=candidate,
        syntactic_valid=True,
        parsed_datetime=parsed,
        parse_mode=parse_mode,
        warnings=warnings,
    )


def parse_javascript_date(cleaned_output: str) -> ParseResult:
    warnings: list[str] = []
    candidate = cleaned_output.strip()
    if not JAVASCRIPT_DATE_RE.match(candidate):
        try:
            parsed = datetime.strptime(candidate, "%a %b %d %Y %H:%M:%S GMT%z")
        except ValueError:
            return ParseResult(cleaned_output=candidate, syntactic_valid=False)
        warnings.append("missing_tz_name")
        return ParseResult(
            cleaned_output=candidate,
            syntactic_valid=True,
            parsed_datetime=parsed,
            parse_mode="loose",
            warnings=warnings,
        )
    core = re.sub(r" \(.+\)$", "", candidate)
    try:
        parsed = datetime.strptime(core, "%a %b %d %Y %H:%M:%S GMT%z")
    except ValueError:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    return ParseResult(
        cleaned_output=candidate,
        syntactic_valid=True,
        parsed_datetime=parsed,
        parse_mode="strict",
    )


def parse_python_datetime(cleaned_output: str) -> ParseResult:
    warnings: list[str] = []
    candidate = cleaned_output.strip()
    if not PYTHON_DATETIME_RE.match(candidate):
        if candidate and "T" in candidate:
            warnings.append("iso_separator")
        return ParseResult(cleaned_output=candidate, syntactic_valid=False, warnings=warnings)
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False, warnings=warnings)
    if parsed.tzinfo is None:
        return ParseResult(cleaned_output=candidate, syntactic_valid=False, warnings=warnings)
    return ParseResult(
        cleaned_output=candidate,
        syntactic_valid=True,
        parsed_datetime=parsed,
        parse_mode="strict",
        warnings=warnings,
    )


def parse_unix_epoch(cleaned_output: str) -> ParseResult:
    warnings: list[str] = []
    candidate = cleaned_output.strip()
    if not UNIX_EPOCH_RE.match(candidate):
        return ParseResult(cleaned_output=candidate, syntactic_valid=False)
    parse_mode = "strict"
    epoch_value = int(candidate)
    if len(candidate.lstrip("-")) == 13:
        epoch_seconds = epoch_value / 1000
        warnings.append("milliseconds_epoch")
        parse_mode = "loose"
    else:
        epoch_seconds = float(epoch_value)
    try:
        parsed = datetime.fromtimestamp(epoch_seconds, tz=UTC)
    except (OverflowError, OSError, ValueError):
        return ParseResult(cleaned_output=candidate, syntactic_valid=False, warnings=warnings)
    return ParseResult(
        cleaned_output=candidate,
        syntactic_valid=True,
        parsed_datetime=parsed,
        parse_mode=parse_mode,
        warnings=warnings,
    )


def parse_multiple_choice(cleaned_output: str, case: PromptCase) -> ParseResult:
    candidate = cleaned_output.strip()
    upper = candidate.upper()
    options = case.metadata.get("options") or {}
    if re.fullmatch(r"[A-D]", upper):
        return ParseResult(
            cleaned_output=upper,
            syntactic_valid=True,
            parse_mode="choice_letter",
            selected_choice=upper,
            selected_option_content=options.get(upper),
        )
    if re.fullmatch(r"[A-D][).]", upper):
        letter = upper[0]
        return ParseResult(
            cleaned_output=letter,
            syntactic_valid=True,
            parse_mode="choice_letter_with_suffix",
            warnings=["suffix_choice_format"],
            selected_choice=letter,
            selected_option_content=options.get(letter),
        )
    for letter, content in options.items():
        if candidate == content:
            return ParseResult(
                cleaned_output=candidate,
                syntactic_valid=False,
                parse_mode="option_content",
                selected_choice=letter,
                selected_option_content=content,
                warnings=["returned_option_content"],
            )
    return ParseResult(cleaned_output=candidate, syntactic_valid=False)


def extract_weekday(cleaned_output: str, format_key: str) -> str | None:
    if format_key == "rfc_2822":
        match = DAY_ABBR_RE.search(cleaned_output)
        return match.group(1).title() if match else None
    if format_key == "javascript_date":
        match = DAY_ABBR_SPACE_RE.search(cleaned_output)
        return match.group(1).title() if match else None
    if format_key == "natural_language":
        match = DAY_FULL_RE.search(cleaned_output)
        return match.group(1).title() if match else None
    return None


def has_weekday_token(cleaned_output: str) -> bool:
    return bool(DAY_ABBR_RE.search(cleaned_output) or DAY_ABBR_SPACE_RE.search(cleaned_output) or DAY_FULL_RE.search(cleaned_output))
