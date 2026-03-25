# AI-ANCHOR: datetime-bench: aggregate analysis and reporting
"""Post-run analysis for the datetime benchmark."""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Any

from .config import (
    COST_REPORT_CSV,
    ERROR_TAXONOMY_CSV,
    FORMAT_COMPARISON_CSV,
    MODEL_SELECTION_FILE,
    PRIMARY_RESULTS_CSV,
    RAW_RESULTS_CSV,
    REPORTS_DIR,
    RESULTS_DIR,
    RUN_MANIFEST_FILE,
    RUN_SUMMARY_FILE,
    SUMMARY_MD,
)


def load_results(results_dir: Path = RESULTS_DIR) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not results_dir.exists():
        return rows
    for path in sorted(results_dir.glob("*.jsonl")):
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
    return rows


def load_selections(path: Path = MODEL_SELECTION_FILE) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_run_summary(path: Path = RUN_SUMMARY_FILE) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def load_run_manifest(path: Path = RUN_MANIFEST_FILE) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row.keys()})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_analysis(
    results_dir: Path = RESULTS_DIR,
    output_dir: Path = REPORTS_DIR,
    *,
    selections: list[dict[str, Any]] | None = None,
    run_summary: dict[str, Any] | None = None,
    run_manifest: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rows = load_results(results_dir)
    selections = selections if selections is not None else load_selections()
    run_summary = run_summary if run_summary is not None else load_run_summary()
    run_manifest = run_manifest if run_manifest is not None else load_run_manifest()
    if not rows:
        msg = (
            f"No result rows found in {results_dir}. "
            "Refusing to regenerate reports from an empty or missing run directory."
        )
        raise RuntimeError(msg)
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_results_csv = output_dir / RAW_RESULTS_CSV.name
    primary_results_csv = output_dir / PRIMARY_RESULTS_CSV.name
    format_comparison_csv = output_dir / FORMAT_COMPARISON_CSV.name
    format_comparison_string_only_csv = output_dir / "format_comparison_string_only.csv"
    epoch_summary_csv = output_dir / "epoch_summary.csv"
    input_variant_summary_csv = output_dir / "input_variant_summary.csv"
    error_taxonomy_csv = output_dir / ERROR_TAXONOMY_CSV.name
    cost_report_csv = output_dir / COST_REPORT_CSV.name
    summary_md_path = output_dir / SUMMARY_MD.name

    flat_rows = _flatten_rows(rows)
    write_csv(raw_results_csv, flat_rows)

    primary_rows = _primary_results(rows)
    write_csv(primary_results_csv, primary_rows)

    format_rows = _format_comparison(rows)
    write_csv(format_comparison_csv, format_rows)

    string_only_rows = [row for row in rows if row.get("format") != "unix_epoch"]
    string_only_format_rows = _format_comparison(string_only_rows)
    write_csv(format_comparison_string_only_csv, string_only_format_rows)

    epoch_rows = _epoch_summary(rows)
    write_csv(epoch_summary_csv, epoch_rows)

    input_variant_rows = _input_variant_summary(rows)
    write_csv(input_variant_summary_csv, input_variant_rows)

    error_rows = _error_taxonomy(rows)
    write_csv(error_taxonomy_csv, error_rows)

    cost_rows = _cost_report(rows, selections, run_summary)
    write_csv(cost_report_csv, cost_rows)

    mode_rows = _mode_format_summary(rows, selections)
    size_rows = _size_format_summary(rows, selections)
    task_sensitivity_rows = _task_sensitivity(rows)
    format_error_rows = _format_error_summary(rows)
    stats = _pairwise_format_tests(rows)
    recommendations = _recommendations(
        format_rows=format_rows,
        string_format_rows=string_only_format_rows,
        mode_rows=mode_rows,
        size_rows=size_rows,
        task_sensitivity_rows=task_sensitivity_rows,
        format_error_rows=format_error_rows,
        stats=stats,
        cost_rows=cost_rows,
    )
    summary_md = _render_summary(
        primary_rows=primary_rows,
        primary_results_name=primary_results_csv.name,
        format_rows=format_rows,
        mode_rows=mode_rows,
        size_rows=size_rows,
        task_sensitivity_rows=task_sensitivity_rows,
        format_error_rows=format_error_rows,
        error_rows=error_rows,
        error_taxonomy_name=error_taxonomy_csv.name,
        cost_rows=cost_rows,
        stats=stats,
        run_summary=run_summary,
        run_manifest=run_manifest,
        recommendations=recommendations,
        selections=selections,
    )
    summary_md_path.write_text(summary_md, encoding="utf-8")

    return {
        "rows": len(rows),
        "primary_results_csv": str(primary_results_csv),
        "format_comparison_csv": str(format_comparison_csv),
        "format_comparison_string_only_csv": str(format_comparison_string_only_csv),
        "epoch_summary_csv": str(epoch_summary_csv),
        "input_variant_summary_csv": str(input_variant_summary_csv),
        "error_taxonomy_csv": str(error_taxonomy_csv),
        "cost_report_csv": str(cost_report_csv),
        "summary_md": str(summary_md_path),
        "run_manifest": (run_manifest.get("paths") or {}).get("run_manifest_file"),
        "pairwise_tests": stats,
        "recommendations": recommendations,
    }


def _flatten_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flat: list[dict[str, Any]] = []
    for row in rows:
        item = dict(row)
        item["warnings"] = "|".join(row.get("warnings") or [])
        item["options"] = json.dumps(row.get("options") or {}, sort_keys=True)
        flat.append(item)
    return flat


def _primary_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], dict[str, list[bool]]] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grouped[(row["task_type"], row["format"])][row["model_cell"]].append(bool(row.get("semantic_correct")))
    model_cells = sorted({row["model_cell"] for row in rows})
    out: list[dict[str, Any]] = []
    for (task_type, format_key), cell_map in sorted(grouped.items()):
        result = {"task_type": task_type, "format": format_key}
        for cell in model_cells:
            values = cell_map.get(cell, [])
            result[cell] = round(100 * sum(values) / len(values), 2) if values else None
        out.append(result)
    return out


def _format_comparison(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = defaultdict(list)
    for row in rows:
        grouped[row["format"]].append(row)
    out: list[dict[str, Any]] = []
    for format_key, items in sorted(grouped.items()):
        semantic_values = [bool(item.get("semantic_correct")) for item in items]
        strict_values = [bool(item.get("strict_correct")) for item in items]
        syntactic_values = [bool(item.get("syntactic_valid")) for item in items]
        compliance_values = [float(item.get("format_compliance") or 0.0) for item in items]
        extraction_values = [bool(item.get("extraction_clean")) for item in items]
        calendar_items = [item for item in items if item.get("calendar_consistent") is not None]
        accuracy = sum(semantic_values) / len(semantic_values) if semantic_values else 0.0
        strict_accuracy = sum(strict_values) / len(strict_values) if strict_values else 0.0
        ci_low, ci_high = _wilson_interval(sum(semantic_values), len(semantic_values))
        out.append(
            {
                "format": format_key,
                "n": len(items),
                "overall_accuracy": round(accuracy, 6),
                "strict_accuracy": round(strict_accuracy, 6),
                "accuracy_ci_low": round(ci_low, 6),
                "accuracy_ci_high": round(ci_high, 6),
                "syntactic_validity_rate": round(sum(syntactic_values) / len(syntactic_values), 6),
                "calendar_consistency_rate": round(
                    sum(bool(item.get("calendar_consistent")) for item in calendar_items) / len(calendar_items),
                    6,
                )
                if calendar_items
                else None,
                "format_compliance_mean": round(mean(compliance_values), 6) if compliance_values else None,
                "extraction_cleanliness_rate": round(sum(extraction_values) / len(extraction_values), 6),
            }
        )
    return out


def _error_taxonomy(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = defaultdict(int)
    for row in rows:
        if row.get("semantic_correct"):
            continue
        grouped[(row["format"], row["model_cell"], row.get("error_type") or "unknown")] += 1
    out = [
        {
            "format": format_key,
            "model_cell": model_cell,
            "error_type": error_type,
            "count": count,
        }
        for (format_key, model_cell, error_type), count in sorted(grouped.items())
    ]
    return out


def _mode_format_summary(
    rows: list[dict[str, Any]],
    selections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped = defaultdict(lambda: [0, 0, 0])
    mode_by_cell, _ = _selection_maps(selections)
    for row in rows:
        key = (_cell_mode(row["model_cell"], mode_by_cell), row["format"])
        grouped[key][0] += 1
        grouped[key][1] += 1 if row.get("semantic_correct") else 0
        grouped[key][2] += 1 if row.get("strict_correct") else 0
    out = []
    for (mode, format_key), (total, correct, strict_correct) in sorted(grouped.items()):
        out.append(
            {
                "mode": mode,
                "format": format_key,
                "accuracy": round(correct / total, 6) if total else 0.0,
                "strict_accuracy": round(strict_correct / total, 6) if total else 0.0,
                "n": total,
                "correct": correct,
                "strict_correct": strict_correct,
            }
        )
    return out


def _size_format_summary(
    rows: list[dict[str, Any]],
    selections: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    grouped = defaultdict(lambda: [0, 0, 0])
    _, size_by_cell = _selection_maps(selections)
    for row in rows:
        key = (_cell_size(row["model_cell"], size_by_cell), row["format"])
        grouped[key][0] += 1
        grouped[key][1] += 1 if row.get("semantic_correct") else 0
        grouped[key][2] += 1 if row.get("strict_correct") else 0
    out = []
    for (size, format_key), (total, correct, strict_correct) in sorted(grouped.items()):
        out.append(
            {
                "size": size,
                "format": format_key,
                "accuracy": round(correct / total, 6) if total else 0.0,
                "strict_accuracy": round(strict_correct / total, 6) if total else 0.0,
                "n": total,
                "correct": correct,
                "strict_correct": strict_correct,
            }
        )
    return out


def _task_sensitivity(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = defaultdict(lambda: [0, 0])
    task_types = sorted({row["task_type"] for row in rows})
    format_keys = sorted({row["format"] for row in rows})
    for row in rows:
        key = (row["task_type"], row["format"])
        grouped[key][0] += 1
        grouped[key][1] += 1 if row.get("semantic_correct") else 0
    out = []
    for task_type in task_types:
        per_format = []
        for format_key in format_keys:
            total, correct = grouped[(task_type, format_key)]
            accuracy = correct / total if total else 0.0
            per_format.append((format_key, accuracy))
        ranked = sorted(per_format, key=lambda item: item[1], reverse=True)
        best_format, best_accuracy = ranked[0]
        worst_format, worst_accuracy = ranked[-1]
        out.append(
            {
                "task_type": task_type,
                "best_format": best_format,
                "best_accuracy": round(best_accuracy, 6),
                "worst_format": worst_format,
                "worst_accuracy": round(worst_accuracy, 6),
                "spread": round(best_accuracy - worst_accuracy, 6),
            }
        )
    return sorted(out, key=lambda item: item["spread"], reverse=True)


def _format_error_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = defaultdict(int)
    for row in rows:
        if row.get("semantic_correct"):
            continue
        grouped[(row["format"], row.get("error_type") or "unknown")] += 1
    by_format = defaultdict(list)
    for (format_key, error_type), count in sorted(grouped.items()):
        by_format[format_key].append((error_type, count))
    out = []
    for format_key, items in sorted(by_format.items()):
        ranked = sorted(items, key=lambda item: item[1], reverse=True)
        top_errors = ranked[:3]
        out.append(
            {
                "format": format_key,
                "top_errors": top_errors,
            }
        )
    return out


def _epoch_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    epoch_rows = [row for row in rows if row.get("format") == "unix_epoch"]
    if not epoch_rows:
        return []
    out = [
        {
            "category": "overall",
            "name": "unix_epoch",
            "n": len(epoch_rows),
            "accuracy": round(sum(bool(row.get("semantic_correct")) for row in epoch_rows) / len(epoch_rows), 6),
            "strict_accuracy": round(sum(bool(row.get("strict_correct")) for row in epoch_rows) / len(epoch_rows), 6),
        }
    ]
    grouped = defaultdict(list)
    for row in epoch_rows:
        grouped[row["task_type"]].append(row)
    for task_type, items in sorted(grouped.items()):
        out.append(
            {
                "category": "task_type",
                "name": task_type,
                "n": len(items),
                "accuracy": round(sum(bool(row.get("semantic_correct")) for row in items) / len(items), 6),
                "strict_accuracy": round(sum(bool(row.get("strict_correct")) for row in items) / len(items), 6),
            }
        )
    return out


def _input_variant_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped = defaultdict(lambda: [0, 0])
    for row in rows:
        input_style = row.get("input_style")
        timezone_representation = row.get("timezone_representation")
        if not input_style or not timezone_representation:
            continue
        key = (row["format"], input_style, timezone_representation)
        grouped[key][0] += 1
        grouped[key][1] += 1 if row.get("semantic_correct") else 0
    out = []
    for (format_key, input_style, timezone_representation), (total, correct) in sorted(grouped.items()):
        out.append(
            {
                "format": format_key,
                "input_style": input_style,
                "timezone_representation": timezone_representation,
                "n": total,
                "accuracy": round(correct / total, 6) if total else 0.0,
            }
        )
    return out


def _cost_report(
    rows: list[dict[str, Any]],
    selections: list[dict[str, Any]],
    run_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    total_cost = sum(float(row.get("estimated_cost_usd") or 0.0) for row in rows)
    out.append({"category": "total", "name": "all", "cost_usd": round(total_cost, 6)})
    per_model = defaultdict(float)
    per_task = defaultdict(float)
    for row in rows:
        cost = float(row.get("estimated_cost_usd") or 0.0)
        per_model[row["model_cell"]] += cost
        per_task[row["task_type"]] += cost
    for model_cell, cost in sorted(per_model.items()):
        out.append({"category": "model_cell", "name": model_cell, "cost_usd": round(cost, 6)})
    for task_type, cost in sorted(per_task.items()):
        out.append({"category": "task_type", "name": task_type, "cost_usd": round(cost, 6)})
    skipped = run_summary.get("skipped_cells") or []
    for item in skipped:
        out.append(
            {
                "category": "skipped_cell",
                "name": item.get("cell"),
                "cost_usd": 0.0,
                "reason": item.get("reason"),
            }
        )
    for selection in selections:
        if not selection.get("selected_model"):
            out.append(
                {
                    "category": "unavailable_cell",
                    "name": selection.get("cell"),
                    "cost_usd": 0.0,
                    "reason": ";".join(selection.get("notes") or []),
                }
            )
    return out


def _pairwise_format_tests(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    counts = defaultdict(lambda: {"success": 0, "failure": 0})
    for row in rows:
        key = row["format"]
        if row.get("semantic_correct"):
            counts[key]["success"] += 1
        else:
            counts[key]["failure"] += 1
    formats = sorted(counts)
    out: list[dict[str, Any]] = []
    for index, left in enumerate(formats):
        for right in formats[index + 1 :]:
            a = counts[left]["success"]
            b = counts[left]["failure"]
            c = counts[right]["success"]
            d = counts[right]["failure"]
            p_value, test_name = _chi_square_or_fisher(a, b, c, d)
            out.append(
                {
                    "left_format": left,
                    "right_format": right,
                    "left_success": a,
                    "left_failure": b,
                    "right_success": c,
                    "right_failure": d,
                    "test": test_name,
                    "p_value": p_value,
                }
            )
    return out


def _chi_square_or_fisher(a: int, b: int, c: int, d: int) -> tuple[float, str]:
    try:
        from scipy.stats import chi2_contingency, fisher_exact  # type: ignore

        table = [[a, b], [c, d]]
        expected_small = any(value < 5 for row in chi2_contingency(table, correction=False)[3] for value in row)
        if expected_small:
            _, p_value = fisher_exact(table)
            return float(p_value), "fisher_exact"
        chi2, p_value, _, _ = chi2_contingency(table, correction=False)
        return float(p_value), "chi_squared"
    except Exception:
        total = a + b + c + d
        if total == 0:
            return 1.0, "chi_squared_manual"
        row1 = a + b
        row2 = c + d
        col1 = a + c
        col2 = b + d
        expected = [
            row1 * col1 / total,
            row1 * col2 / total,
            row2 * col1 / total,
            row2 * col2 / total,
        ]
        observed = [a, b, c, d]
        chi2 = 0.0
        for obs, exp in zip(observed, expected, strict=True):
            if exp:
                chi2 += (obs - exp) ** 2 / exp
        p_value = math.erfc(math.sqrt(chi2 / 2.0))
        return float(p_value), "chi_squared_manual"


def _recommendations(
    *,
    format_rows: list[dict[str, Any]],
    string_format_rows: list[dict[str, Any]],
    mode_rows: list[dict[str, Any]],
    size_rows: list[dict[str, Any]],
    task_sensitivity_rows: list[dict[str, Any]],
    format_error_rows: list[dict[str, Any]],
    stats: list[dict[str, Any]],
    cost_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    ranked = sorted(string_format_rows, key=lambda row: row.get("overall_accuracy") or 0.0, reverse=True)
    best = ranked[0] if ranked else None
    rfc_3339 = next((row for row in string_format_rows if row["format"] == "rfc_3339"), None)
    tests_for_best = [
        item for item in stats if best and best["format"] in {item["left_format"], item["right_format"]}
    ]
    size_rankings = []
    for size in sorted({row["size"] for row in size_rows}):
        rows_for_size = [row for row in size_rows if row["size"] == size]
        ranked_size = sorted(rows_for_size, key=lambda row: row["accuracy"], reverse=True)
        size_rankings.append(
            {
                "size": size,
                "best_format": ranked_size[0]["format"],
                "rows": ranked_size,
            }
        )
    reasoning_deltas = []
    for format_key in sorted({row["format"] for row in mode_rows}):
        reasoning_row = next(
            (row for row in mode_rows if row["mode"] == "reasoning" and row["format"] == format_key), None
        )
        non_reasoning_row = next(
            (row for row in mode_rows if row["mode"] == "non_reasoning" and row["format"] == format_key), None
        )
        if reasoning_row is None or non_reasoning_row is None:
            continue
        reasoning_deltas.append(
            {
                "format": format_key,
                "reasoning_accuracy": reasoning_row["accuracy"],
                "non_reasoning_accuracy": non_reasoning_row["accuracy"],
                "delta": round(reasoning_row["accuracy"] - non_reasoning_row["accuracy"], 6),
            }
        )
    total_cost = next((row["cost_usd"] for row in cost_rows if row["category"] == "total"), 0.0)
    if (
        best
        and rfc_3339
        and best["format"] in {"iso_8601", "rfc_3339", "python_datetime"}
        and (
            best["format"] == "rfc_3339"
            or _is_statistically_tied(best["format"], "rfc_3339", stats)
        )
    ):
        system_prompt_recommendation = (
            "Use `RFC 3339` as the default machine-facing timestamp format. "
            "It is statistically tied with the top cluster and names an unambiguous spec."
        )
    else:
        system_prompt_recommendation = (
            "Use the top-ranked format from the benchmark for system-prompted timestamp generation."
        )
    return {
        "best_format": best["format"] if best else None,
        "best_accuracy": best.get("overall_accuracy") if best else None,
        "best_confidence_interval": (
            best.get("accuracy_ci_low"),
            best.get("accuracy_ci_high"),
        )
        if best
        else None,
        "significance_tests": tests_for_best,
        "size_rankings": size_rankings,
        "reasoning_deltas": reasoning_deltas,
        "most_sensitive_tasks": task_sensitivity_rows[:3],
        "format_error_rows": format_error_rows,
        "system_prompt_recommendation": system_prompt_recommendation,
        "total_cost_usd": total_cost,
    }


def _wilson_interval(successes: int, total: int, z: float = 1.96) -> tuple[float, float]:
    if total == 0:
        return 0.0, 0.0
    phat = successes / total
    denominator = 1 + z**2 / total
    center = (phat + z**2 / (2 * total)) / denominator
    margin = (
        z
        * math.sqrt((phat * (1 - phat) + z**2 / (4 * total)) / total)
        / denominator
    )
    return max(0.0, center - margin), min(1.0, center + margin)


def _selection_maps(
    selections: list[dict[str, Any]],
) -> tuple[dict[str, str], dict[str, str]]:
    mode_by_cell: dict[str, str] = {}
    size_by_cell: dict[str, str] = {}
    for item in selections:
        cell = str(item.get("cell") or "")
        if not cell:
            continue
        mode = item.get("reasoning_mode")
        size = item.get("size")
        if isinstance(mode, str) and mode:
            mode_by_cell[cell] = mode
        if isinstance(size, str) and size:
            size_by_cell[cell] = size
    return mode_by_cell, size_by_cell


def _is_statistically_tied(left: str, right: str, stats: list[dict[str, Any]], alpha: float = 0.05) -> bool:
    if left == right:
        return True
    match = next(
        (
            item
            for item in stats
            if {item["left_format"], item["right_format"]} == {left, right}
        ),
        None,
    )
    if match is None:
        return False
    return float(match["p_value"]) >= alpha


def _render_summary(
    *,
    primary_rows: list[dict[str, Any]],
    primary_results_name: str,
    format_rows: list[dict[str, Any]],
    mode_rows: list[dict[str, Any]],
    size_rows: list[dict[str, Any]],
    task_sensitivity_rows: list[dict[str, Any]],
    format_error_rows: list[dict[str, Any]],
    error_rows: list[dict[str, Any]],
    error_taxonomy_name: str,
    cost_rows: list[dict[str, Any]],
    stats: list[dict[str, Any]],
    run_summary: dict[str, Any],
    run_manifest: dict[str, Any],
    recommendations: dict[str, Any],
    selections: list[dict[str, Any]],
) -> str:
    lines = ["# Datetime Format Benchmark Summary", ""]
    if run_manifest:
        lines.append("## Run Metadata")
        metadata_rows = [
            ["Version", run_manifest.get("version") or "-"],
            ["Previous Version", run_manifest.get("previous_version") or "-"],
            ["Run Slug", run_manifest.get("run_slug") or "-"],
            ["Report Slug", run_manifest.get("report_slug") or "-"],
            ["Seed", run_manifest.get("seed")],
            ["Max Tokens", run_manifest.get("max_tokens")],
            ["Soft Cap USD", run_manifest.get("soft_cap_usd")],
            ["Hard Cap USD", run_manifest.get("hard_cap_usd")],
            ["Resume", run_manifest.get("resume")],
            ["Dry Run Cached", run_manifest.get("dry_run_cached")],
            ["Git SHA", run_manifest.get("git_sha") or "-"],
        ]
        lines.append(_markdown_table(["Field", "Value"], metadata_rows))
        lines.append("")

    lines.append("## Model Selection")
    model_table = [
        [
            item.get("cell"),
            item.get("selected_model") or "SKIPPED",
            item.get("reasoning_mode"),
            "; ".join(item.get("notes") or []),
        ]
        for item in selections
    ]
    lines.append(_markdown_table(["Cell", "Selected Model", "Mode", "Notes"], model_table))
    lines.append("")

    lines.append("## Headline Format Comparison")
    lines.append(
        _markdown_table(
            [
                "Format",
                "Accuracy",
                "Strict",
                "95% CI",
                "Syntactic",
                "Calendar",
                "Compliance",
                "Clean",
            ],
            [
                [
                    row["format"],
                    _pct(row["overall_accuracy"]),
                    _pct(row["strict_accuracy"]),
                    f"{_pct(row['accuracy_ci_low'])} to {_pct(row['accuracy_ci_high'])}",
                    _pct(row["syntactic_validity_rate"]),
                    _pct(row["calendar_consistency_rate"]),
                    f"{row['format_compliance_mean']:.3f}" if row.get("format_compliance_mean") is not None else "-",
                    _pct(row["extraction_cleanliness_rate"]),
                ]
                for row in format_rows
            ],
        )
    )
    lines.append("")

    lines.append("## Primary Results")
    primary_headers = list(primary_rows[0].keys()) if primary_rows else ["task_type", "format"]
    primary_table = [[row.get(key) for key in primary_headers] for row in primary_rows[:30]]
    lines.append(_markdown_table(primary_headers, primary_table))
    if len(primary_rows) > 30:
        lines.append("")
        lines.append(f"Truncated in summary; full table is in `{primary_results_name}`.")
    lines.append("")

    lines.append("## Pairwise Format Tests")
    stats_table = [
        [item["left_format"], item["right_format"], item["test"], f"{item['p_value']:.6g}"]
        for item in stats
    ]
    lines.append(_markdown_table(["Left", "Right", "Test", "p-value"], stats_table))
    lines.append("")

    lines.append("## Interaction Highlights")
    mode_table = [
        [row["mode"], row["format"], _pct(row["accuracy"]), _pct(row["strict_accuracy"]), row["correct"], row["n"]]
        for row in mode_rows
    ]
    lines.append(_markdown_table(["Mode", "Format", "Accuracy", "Strict", "Correct", "N"], mode_table))
    lines.append("")
    size_table = [
        [row["size"], row["format"], _pct(row["accuracy"]), _pct(row["strict_accuracy"]), row["correct"], row["n"]]
        for row in size_rows
    ]
    lines.append(_markdown_table(["Size", "Format", "Accuracy", "Strict", "Correct", "N"], size_table))
    lines.append("")
    task_table = [
        [
            row["task_type"],
            row["best_format"],
            _pct(row["best_accuracy"]),
            row["worst_format"],
            _pct(row["worst_accuracy"]),
            _pct(row["spread"]),
        ]
        for row in task_sensitivity_rows[:7]
    ]
    lines.append(
        _markdown_table(
            ["Task Type", "Best Format", "Best Accuracy", "Worst Format", "Worst Accuracy", "Spread"],
            task_table,
        )
    )
    lines.append("")

    lines.append("## Error Taxonomy")
    error_table = [
        [row["format"], row["model_cell"], row["error_type"], row["count"]]
        for row in error_rows[:30]
    ]
    lines.append(_markdown_table(["Format", "Model Cell", "Error Type", "Count"], error_table))
    if len(error_rows) > 30:
        lines.append("")
        lines.append(f"Truncated in summary; full table is in `{error_taxonomy_name}`.")
    lines.append("")

    lines.append("## Cost Report")
    cost_table = [
        [row.get("category"), row.get("name"), row.get("cost_usd"), row.get("reason", "")]
        for row in cost_rows
    ]
    lines.append(_markdown_table(["Category", "Name", "Cost USD", "Reason"], cost_table))
    lines.append("")

    lines.append("## Recommendations")
    best_format = recommendations.get("best_format")
    best_accuracy = recommendations.get("best_accuracy")
    ci = recommendations.get("best_confidence_interval")
    if best_format:
        lines.append(
            f"- Highest string-format reliability: `{best_format}` at {_pct(best_accuracy)} "
            f"with 95% CI {_pct(ci[0])} to {_pct(ci[1])}."
        )
    else:
        lines.append("- Highest string-format reliability: insufficient data.")
    for item in recommendations.get("significance_tests") or []:
        comparator = item["right_format"] if item["left_format"] == best_format else item["left_format"]
        lines.append(
            f"- `{best_format}` vs `{comparator}`: {item['test']} p-value = {item['p_value']:.6g}."
        )
    for item in recommendations.get("size_rankings") or []:
        ranking = ", ".join(f"{row['format']} {_pct(row['accuracy'])}" for row in item["rows"])
        lines.append(f"- Size `{item['size']}` ranking: {ranking}.")
    for item in recommendations.get("reasoning_deltas") or []:
        lines.append(
            f"- Reasoning delta for `{item['format']}`: {_pct(item['reasoning_accuracy'])} vs "
            f"{_pct(item['non_reasoning_accuracy'])} (`+{item['delta'] * 100:.2f}` points)."
        )
    most_sensitive = recommendations.get("most_sensitive_tasks") or []
    if most_sensitive:
        lines.append(
            "- Most format-sensitive tasks: "
            + "; ".join(
                f"`{item['task_type']}` ({item['best_format']} {_pct(item['best_accuracy'])} vs "
                f"{item['worst_format']} {_pct(item['worst_accuracy'])})"
                for item in most_sensitive
            )
            + "."
        )
    lines.append(f"- System-prompt recommendation: {recommendations['system_prompt_recommendation']}")
    lines.append("- Main recommendation surface: string formats only. `unix_epoch` is reported separately.")
    lines.append("- `unix_epoch` is analyzed separately from string formats for default-format recommendations.")
    lines.append(
        "- Reasoning vs non-reasoning summaries reflect the configured production request shapes "
        "(temperature 1.0 vs 0.0), not an isolated causal reasoning estimate."
    )
    for item in recommendations.get("format_error_rows") or []:
        error_summary = ", ".join(f"{name} ({count})" for name, count in item["top_errors"])
        lines.append(f"- Common `{item['format']}` error modes: {error_summary}.")
    lines.append(f"- Total benchmark spend: ${recommendations['total_cost_usd']:.6f}.")
    skipped = run_summary.get("skipped_cells") or []
    if skipped:
        lines.append("- Budget or availability skips:")
        for item in skipped:
            lines.append(f"  - `{item.get('cell')}`: {item.get('reason')}")
    return "\n".join(lines) + "\n"


def _markdown_table(headers: list[str], rows: list[list[Any]]) -> str:
    if not rows:
        rows = [["-" for _ in headers]]
    normalized_rows = [["-" if value is None else str(value) for value in row] for row in rows]
    widths = [len(str(header)) for header in headers]
    for row in normalized_rows:
        for idx, value in enumerate(row):
            widths[idx] = max(widths[idx], len(value))
    def render(row: list[str]) -> str:
        return "| " + " | ".join(value.ljust(widths[idx]) for idx, value in enumerate(row)) + " |"
    lines = [render(headers), render(["-" * width for width in widths])]
    lines.extend(render(row) for row in normalized_rows)
    return "\n".join(lines)


def _pct(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.2f}%"


def _cell_mode(model_cell: str, mode_by_cell: dict[str, str] | None = None) -> str:
    if mode_by_cell and model_cell in mode_by_cell:
        return mode_by_cell[model_cell]
    tokens = model_cell.split("_")
    if "nr" in tokens:
        return "non_reasoning"
    if "r" in tokens:
        return "reasoning"
    return "unknown"


def _cell_size(model_cell: str, size_by_cell: dict[str, str] | None = None) -> str:
    if size_by_cell and model_cell in size_by_cell:
        return size_by_cell[model_cell]
    tokens = model_cell.split("_")
    for token in tokens:
        if token == "med":
            return "medium"
        if token in {"small", "medium", "large"}:
            return token
    return "unknown"
