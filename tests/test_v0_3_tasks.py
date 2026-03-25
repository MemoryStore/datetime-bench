import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from datetime_bench.analysis import _epoch_summary, _input_variant_summary
from datetime_bench.config import TASKS_PER_TYPE_MAP
from datetime_bench.tasks import generate_all_tasks


class V03TaskTests(unittest.TestCase):
    def test_generate_all_tasks_uses_parsing_normalization_family(self) -> None:
        tasks = generate_all_tasks(seed=42)
        counts = {}
        for task in tasks:
            counts[task.task_type] = counts.get(task.task_type, 0) + 1

        self.assertNotIn("multiple_choice_validation", counts)
        self.assertEqual(counts["parsing_normalization"], TASKS_PER_TYPE_MAP["parsing_normalization"])

    def test_parsing_normalization_tasks_carry_variant_metadata(self) -> None:
        tasks = generate_all_tasks(seed=42)
        parsing_tasks = [task for task in tasks if task.task_type == "parsing_normalization"]

        self.assertTrue(parsing_tasks)
        for task in parsing_tasks:
            self.assertIn("input_style", task.metadata)
            self.assertIn("timezone_representation", task.metadata)
            self.assertIn("source_representation", task.metadata)


class V03AnalysisTests(unittest.TestCase):
    def test_epoch_summary_groups_overall_and_task(self) -> None:
        rows = [
            {"format": "unix_epoch", "task_type": "direct_generation", "semantic_correct": True, "strict_correct": True},
            {"format": "unix_epoch", "task_type": "direct_generation", "semantic_correct": False, "strict_correct": False},
            {"format": "iso_8601", "task_type": "direct_generation", "semantic_correct": True, "strict_correct": True},
        ]
        summary = _epoch_summary(rows)

        self.assertEqual(summary[0]["category"], "overall")
        self.assertEqual(summary[0]["n"], 2)
        self.assertEqual(summary[1]["category"], "task_type")
        self.assertEqual(summary[1]["name"], "direct_generation")

    def test_input_variant_summary_uses_metadata_fields(self) -> None:
        rows = [
            {
                "format": "rfc_3339",
                "input_style": "canonical_text",
                "timezone_representation": "iana_zone",
                "semantic_correct": True,
            },
            {
                "format": "rfc_3339",
                "input_style": "canonical_text",
                "timezone_representation": "iana_zone",
                "semantic_correct": False,
            },
            {
                "format": "rfc_3339",
                "semantic_correct": True,
            },
        ]
        summary = _input_variant_summary(rows)

        self.assertEqual(len(summary), 1)
        self.assertEqual(summary[0]["n"], 2)
        self.assertEqual(summary[0]["accuracy"], 0.5)


if __name__ == "__main__":
    unittest.main()
