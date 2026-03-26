#!/usr/bin/env python3
"""Render quick-look README figures for a versioned report snapshot."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import PercentFormatter

TEXT = "#1f2937"
GRID = "#d1d5db"
FIG_BG = "#f7f7f5"
AX_BG = "#ffffff"
EDGE = "#374151"
PREFERRED = "#009E73"
ACCEPTABLE = "#E69F00"
AVOID = "#D55E00"
TOP3_COLORS = {
    "rfc_3339": "#0072B2",
    "iso_8601": "#009E73",
    "python_datetime": "#CC79A7",
}
FORMAT_LABELS = {
    "rfc_3339": "RFC 3339",
    "iso_8601": "ISO 8601",
    "python_datetime": "Python datetime",
    "rfc_2822": "RFC 2822",
    "javascript_date": "JavaScript Date",
    "natural_language": "Natural language",
    "unix_epoch": "Unix epoch",
}
TZ_LABELS = {
    "utc_or_z": "UTC / Z",
    "numeric_offset": "Numeric offset",
    "iana_zone": "IANA zone",
    "abbr_or_gmt": "Abbr / GMT",
}
FORMAT_ORDER = [
    "rfc_3339",
    "iso_8601",
    "python_datetime",
    "rfc_2822",
    "javascript_date",
    "natural_language",
    "unix_epoch",
]
TZ_ORDER = ["utc_or_z", "numeric_offset", "iana_zone", "abbr_or_gmt"]
TOP_FORMATS = ["rfc_3339", "iso_8601", "python_datetime"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def apply_style() -> None:
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.titlesize": 16,
            "axes.labelsize": 11,
            "axes.facecolor": AX_BG,
            "axes.edgecolor": EDGE,
            "axes.labelcolor": TEXT,
            "figure.facecolor": FIG_BG,
            "savefig.facecolor": FIG_BG,
            "text.color": TEXT,
            "xtick.color": TEXT,
            "ytick.color": TEXT,
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def render_format_accuracy(report_dir: Path, output_dir: Path) -> None:
    rows = {row["format"]: row for row in read_csv(report_dir / "format_comparison.csv")}
    ordered = [rows[key] for key in FORMAT_ORDER if key in rows]
    positions = [0, 1, 2, 3, 4, 5, 7]
    values = [100 * float(row["overall_accuracy"]) for row in ordered]
    err_low = [100 * (float(row["overall_accuracy"]) - float(row["accuracy_ci_low"])) for row in ordered]
    err_high = [100 * (float(row["accuracy_ci_high"]) - float(row["overall_accuracy"])) for row in ordered]

    colors = []
    for row in ordered:
        format_key = row["format"]
        if format_key in {"rfc_3339", "iso_8601", "python_datetime"}:
            colors.append(PREFERRED)
        elif format_key == "rfc_2822":
            colors.append(ACCEPTABLE)
        else:
            colors.append(AVOID)

    fig, ax = plt.subplots(figsize=(10, 5.8))
    bars = ax.barh(
        positions,
        values,
        color=colors,
        edgecolor=EDGE,
        linewidth=0.8,
        xerr=[err_low, err_high],
        error_kw={"elinewidth": 1.2, "ecolor": EDGE, "capsize": 3},
    )
    ax.set_yticks(positions)
    ax.set_yticklabels([FORMAT_LABELS[row["format"]] for row in ordered])
    ax.set_xlim(0, 100)
    ax.xaxis.set_major_formatter(PercentFormatter())
    ax.grid(axis="x", color=GRID, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    ax.invert_yaxis()
    ax.set_xlabel("Semantic accuracy")
    fig.suptitle("Datetime output reliability by format", y=0.975, fontsize=20, fontweight="bold")
    fig.text(
        0.125,
        0.905,
        "v0.3 quick look. Error bars show 95% Wilson confidence intervals. n = 5,170 per format.",
        fontsize=10,
        color="#4b5563",
    )
    ax.axhline(6.1, color=GRID, linewidth=1.2, linestyle="--")
    ax.text(
        60,
        6.55,
        "Separate numeric-conversion problem",
        fontsize=10,
        color="#4b5563",
        ha="left",
        va="center",
    )

    for bar, value in zip(bars, values):
        ax.text(
            min(value + 1.0, 98.0),
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}%",
            va="center",
            ha="left",
            fontsize=10,
            color=TEXT,
        )

    legend_items = [
        Patch(facecolor=PREFERRED, edgecolor=EDGE, label="Recommended"),
        Patch(facecolor=ACCEPTABLE, edgecolor=EDGE, label="Acceptable with caveats"),
        Patch(facecolor=AVOID, edgecolor=EDGE, label="Avoid as default"),
    ]
    fig.legend(handles=legend_items, frameon=False, loc="lower center", ncol=3, bbox_to_anchor=(0.5, 0.01))
    fig.subplots_adjust(top=0.86, bottom=0.16)
    save_figure(fig, output_dir / "format_accuracy")


def render_timezone_impact(report_dir: Path, output_dir: Path) -> None:
    rows = read_csv(report_dir / "results_all.csv")
    grouped: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    for row in rows:
        format_key = row["format"]
        tz_key = row.get("timezone_representation") or ""
        if format_key not in TOP_FORMATS or tz_key not in TZ_ORDER:
            continue
        grouped[(format_key, tz_key)][0] += int(row["semantic_correct"] == "True")
        grouped[(format_key, tz_key)][1] += 1

    width = 0.22
    group_positions = list(range(len(TZ_ORDER)))
    offsets = [-width, 0.0, width]

    fig, ax = plt.subplots(figsize=(10, 5.8))
    for offset, format_key in zip(offsets, TOP_FORMATS):
        heights = []
        xs = []
        for idx, tz_key in enumerate(TZ_ORDER):
            correct, total = grouped[(format_key, tz_key)]
            heights.append(100 * correct / total)
            xs.append(group_positions[idx] + offset)
        bars = ax.bar(
            xs,
            heights,
            width=width,
            color=TOP3_COLORS[format_key],
            edgecolor=EDGE,
            linewidth=0.8,
            label=FORMAT_LABELS[format_key],
        )
        for bar, value in zip(bars, heights):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                value + 1.2,
                f"{value:.1f}%",
                ha="center",
                va="bottom",
                fontsize=9,
                color=TEXT,
            )

    ax.set_xticks(group_positions)
    ax.set_xticklabels([TZ_LABELS[key] for key in TZ_ORDER])
    ax.set_ylim(0, 100)
    ax.yaxis.set_major_formatter(PercentFormatter())
    ax.grid(axis="y", color=GRID, linewidth=0.8, alpha=0.6)
    ax.set_axisbelow(True)
    ax.set_ylabel("Semantic accuracy")
    fig.suptitle(
        "Timezone wording changes accuracy even for the best formats",
        y=0.975,
        fontsize=20,
        fontweight="bold",
    )
    fig.text(
        0.125,
        0.905,
        "Weighted across all tasks and input styles. Normalize abbreviations before the final formatting prompt.",
        fontsize=10,
        color="#4b5563",
    )
    ax.legend(frameon=False, loc="lower left")
    fig.subplots_adjust(top=0.86)
    save_figure(fig, output_dir / "timezone_impact_top3")


def save_figure(fig: plt.Figure, base_path: Path) -> None:
    base_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(base_path.with_suffix(".png"), dpi=220, bbox_inches="tight")
    fig.savefig(base_path.with_suffix(".svg"), bbox_inches="tight")
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--report-dir",
        type=Path,
        default=Path("reports/datetime_bench_v0.3"),
        help="Path to the versioned report directory.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Optional explicit output directory. Defaults to <report-dir>/figures.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    apply_style()
    report_dir = args.report_dir
    output_dir = args.output_dir or report_dir / "figures"
    render_format_accuracy(report_dir, output_dir)
    render_timezone_impact(report_dir, output_dir)


if __name__ == "__main__":
    main()
