import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from datetime_bench.analysis import _mode_format_summary, _size_format_summary, run_analysis
from datetime_bench.config import NON_REASONING_TEMPERATURE, REASONING_TEMPERATURE
from datetime_bench.openrouter import reasoning_control_mode, request_temperature_for_model
from datetime_bench.types import SelectedModel


def _selection(
    *,
    cell: str,
    reasoning_mode: str,
    size: str,
    reasoning_config,
) -> SelectedModel:
    return SelectedModel(
        cell=cell,
        label=cell,
        requested_candidates=["provider/model"],
        selected_model="provider/model",
        reasoning_mode=reasoning_mode,
        size=size,
        reasoning_config=reasoning_config,
        pricing={},
        notes=[],
    )


class RequestContractTests(unittest.TestCase):
    def test_request_temperature_follows_mode(self) -> None:
        non_reasoning = _selection(
            cell="google_small_nr",
            reasoning_mode="non_reasoning",
            size="small",
            reasoning_config=None,
        )
        reasoning = _selection(
            cell="google_small_r",
            reasoning_mode="reasoning",
            size="small",
            reasoning_config={"effort": "minimal"},
        )

        self.assertEqual(request_temperature_for_model(non_reasoning), NON_REASONING_TEMPERATURE)
        self.assertEqual(request_temperature_for_model(reasoning), REASONING_TEMPERATURE)

    def test_reasoning_control_mode_is_explicit(self) -> None:
        explicit_reasoning = _selection(
            cell="google_small_r",
            reasoning_mode="reasoning",
            size="small",
            reasoning_config={"effort": "minimal"},
        )
        explicit_disabled = _selection(
            cell="google_small_nr",
            reasoning_mode="non_reasoning",
            size="small",
            reasoning_config={"enabled": False},
        )
        omitted_provider_default = _selection(
            cell="openai_small_nr",
            reasoning_mode="non_reasoning",
            size="small",
            reasoning_config=None,
        )

        self.assertEqual(reasoning_control_mode(explicit_reasoning), "explicit_reasoning")
        self.assertEqual(reasoning_control_mode(explicit_disabled), "explicit_disabled")
        self.assertEqual(reasoning_control_mode(omitted_provider_default), "omitted_provider_default")


class AnalysisContractTests(unittest.TestCase):
    def test_mode_and_size_summaries_use_declared_metadata(self) -> None:
        rows = [
            {
                "model_cell": "google_small_nr",
                "format": "iso_8601",
                "semantic_correct": True,
                "strict_correct": True,
            },
            {
                "model_cell": "openai_med_nr_chat",
                "format": "iso_8601",
                "semantic_correct": False,
                "strict_correct": False,
            },
        ]
        selections = [
            {"cell": "google_small_nr", "reasoning_mode": "non_reasoning", "size": "small"},
            {"cell": "openai_med_nr_chat", "reasoning_mode": "non_reasoning", "size": "medium"},
        ]

        mode_rows = _mode_format_summary(rows, selections)
        size_rows = _size_format_summary(rows, selections)
        mode_map = {(row["mode"], row["format"]): row for row in mode_rows}
        size_map = {(row["size"], row["format"]): row for row in size_rows}

        self.assertEqual(mode_map[("non_reasoning", "iso_8601")]["n"], 2)
        self.assertEqual(size_map[("small", "iso_8601")]["n"], 1)
        self.assertEqual(size_map[("medium", "iso_8601")]["n"], 1)

    def test_run_analysis_rejects_empty_results(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            results_dir = Path(tmpdir) / "results"
            output_dir = Path(tmpdir) / "reports"
            results_dir.mkdir(parents=True, exist_ok=True)
            with self.assertRaises(RuntimeError):
                run_analysis(results_dir=results_dir, output_dir=output_dir, selections=[])


if __name__ == "__main__":
    unittest.main()
