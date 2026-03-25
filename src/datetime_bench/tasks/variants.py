# AI-ANCHOR: datetime-bench tasks: input diversity helpers
"""Helpers for v0.3 input-style and timezone-representation variants."""

from __future__ import annotations

from datetime import UTC, datetime


INPUT_STYLES = (
    "canonical_text",
    "compact_structured",
    "prose_messy",
    "ambiguous_but_resolved",
)

TIMEZONE_REPRESENTATIONS = (
    "iana_zone",
    "numeric_offset",
    "abbr_or_gmt",
    "utc_or_z",
)


def variant_for_index(index: int) -> tuple[str, str]:
    style = INPUT_STYLES[(index - 1) % len(INPUT_STYLES)]
    timezone_representation = TIMEZONE_REPRESENTATIONS[(index - 1) % len(TIMEZONE_REPRESENTATIONS)]
    return style, timezone_representation


def normalize_timezone_for_representation(dt: datetime, timezone_representation: str) -> datetime:
    if timezone_representation == "utc_or_z":
        return dt.astimezone(UTC)
    return dt


def describe_datetime_variant(
    dt: datetime,
    input_style: str,
    timezone_representation: str,
    *,
    assume_mdy: bool = True,
) -> str:
    date_long = dt.strftime("%B %d, %Y").replace(" 0", " ")
    hour = dt.hour % 12 or 12
    time_12h = f"{hour}:{dt.minute:02d} {'AM' if dt.hour < 12 else 'PM'}"
    time_24h = dt.strftime("%H:%M:%S")
    offset = dt.strftime("%z")
    offset_colon = f"{offset[:3]}:{offset[3:]}" if offset else ""
    iana_zone = dt.tzinfo.key if hasattr(dt.tzinfo, "key") else (dt.tzname() or "UTC")
    abbr = dt.tzname() or offset_colon or "UTC"
    slash_date = dt.strftime("%m/%d/%Y") if assume_mdy else dt.strftime("%d/%m/%Y")

    if timezone_representation == "iana_zone":
        zone_phrase = f"in timezone {iana_zone}"
        compact_zone = iana_zone
        ambiguous_zone = iana_zone
    elif timezone_representation == "numeric_offset":
        zone_phrase = offset_colon
        compact_zone = offset_colon
        ambiguous_zone = offset_colon
    elif timezone_representation == "abbr_or_gmt":
        zone_phrase = abbr if abbr != "UTC" else "GMT+0000"
        compact_zone = zone_phrase
        ambiguous_zone = zone_phrase
    else:
        zone_phrase = "UTC"
        compact_zone = "Z"
        ambiguous_zone = "UTC"

    if input_style == "canonical_text":
        return f"{date_long} at {time_12h} {zone_phrase}".strip()
    if input_style == "compact_structured":
        if timezone_representation == "utc_or_z":
            return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
        return f"{dt.strftime('%Y-%m-%d')} {time_24h} {compact_zone}".strip()
    if input_style == "prose_messy":
        return (
            "The note says the relevant timestamp is "
            f"{date_long} at {time_12h} {zone_phrase}, and the rest of the message is irrelevant."
        ).strip()
    order_note = "month/day/year" if assume_mdy else "day/month/year"
    return f"Assume {order_note} ordering. Parse {slash_date} {time_12h} {ambiguous_zone}.".strip()
