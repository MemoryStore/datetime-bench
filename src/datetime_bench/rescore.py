# AI-ANCHOR: datetime-bench: offline result rescoring
"""Re-evaluate stored JSONL results with the current parser and scoring logic."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .config import DEFAULT_LAYOUT, SEED
from .evaluation import clean_output, evaluate_case, parse_output
from .tasks import load_generated_tasks
from .tasks.base import expand_scenarios


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tasks",
        type=Path,
        default=DEFAULT_LAYOUT.tasks_dir / f"tasks_seed{SEED}.json",
        help="Path to generated task scenarios JSON",
    )
    parser.add_argument(
        "--results-dir",
        type=Path,
        default=DEFAULT_LAYOUT.results_dir,
        help="Directory containing per-cell JSONL result files",
    )
    parser.add_argument(
        "--backup-dir",
        type=Path,
        default=None,
        help="Optional backup directory for pre-rescore JSONL files",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    tasks = load_generated_tasks(args.tasks)
    case_map = {case.case_id: case for case in expand_scenarios(tasks)}

    if args.backup_dir is not None:
        args.backup_dir.mkdir(parents=True, exist_ok=True)

    changed_rows = 0
    total_rows = 0
    for path in sorted(args.results_dir.glob("*.jsonl")):
        rows = [json.loads(line) for line in path.open("r", encoding="utf-8") if line.strip()]
        if args.backup_dir is not None:
            backup_path = args.backup_dir / path.name
            backup_path.write_text(
                "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
                encoding="utf-8",
            )

        updated_rows: list[dict[str, Any]] = []
        for row in rows:
            total_rows += 1
            case = case_map.get(row["case_id"])
            if case is None:
                updated_rows.append(row)
                continue
            rescored = _rescore_row(row, case)
            if rescored != row:
                changed_rows += 1
            updated_rows.append(rescored)

        path.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in updated_rows),
            encoding="utf-8",
        )

    print(json.dumps({"total_rows": total_rows, "changed_rows": changed_rows}, indent=2))
    return 0


def _rescore_row(row: dict[str, Any], case) -> dict[str, Any]:
    raw_output = row.get("raw_output") or ""
    cleaned = clean_output(raw_output)
    parse_result = parse_output(case, cleaned)
    evaluation = evaluate_case(case, raw_output, parse_result)

    updated = dict(row)
    updated["cleaned_output"] = parse_result.cleaned_output
    updated["gold_formatted"] = case.gold_formatted
    updated["syntactic_valid"] = evaluation.syntactic_valid
    updated["semantic_correct"] = evaluation.semantic_correct
    updated["strict_correct"] = evaluation.strict_correct
    updated["calendar_consistent"] = evaluation.calendar_consistent
    updated["format_compliance"] = evaluation.format_compliance
    updated["extraction_clean"] = evaluation.extraction_clean
    updated["error_type"] = evaluation.error_type
    updated["error_subtype"] = evaluation.error_subtype
    updated["delta_seconds"] = evaluation.delta_seconds
    updated["parse_mode"] = evaluation.parse_mode
    updated["warnings"] = evaluation.warnings
    updated["selected_choice"] = evaluation.selected_choice
    updated["selected_option_content"] = evaluation.selected_option_content
    return updated


if __name__ == "__main__":
    raise SystemExit(main())
