# AI-ANCHOR: datetime-bench eval: budget tracker and stop rules
"""Budget accounting for the benchmark run."""

from __future__ import annotations

from collections import defaultdict

from ..config import HARD_BUDGET_CAP_USD, SOFT_BUDGET_CAP_USD


class BudgetTracker:
    """Tracks cumulative spend and exposes soft/hard stop signals."""

    def __init__(
        self,
        soft_cap_usd: float = SOFT_BUDGET_CAP_USD,
        hard_cap_usd: float = HARD_BUDGET_CAP_USD,
    ):
        self.soft_cap_usd = soft_cap_usd
        self.hard_cap_usd = hard_cap_usd
        self.total_spend_usd = 0.0
        self.by_model_cell: dict[str, float] = defaultdict(float)
        self.by_task_type: dict[str, float] = defaultdict(float)
        self.soft_cap_triggered = False
        self.hard_cap_triggered = False

    def record(self, *, model_cell: str, task_type: str, cost_usd: float) -> None:
        self.total_spend_usd += float(cost_usd)
        self.by_model_cell[model_cell] += float(cost_usd)
        self.by_task_type[task_type] += float(cost_usd)
        if self.total_spend_usd >= self.soft_cap_usd:
            self.soft_cap_triggered = True
        if self.total_spend_usd >= self.hard_cap_usd:
            self.hard_cap_triggered = True

    def should_stop_all(self) -> bool:
        return self.hard_cap_triggered

    def summary(self) -> dict[str, object]:
        return {
            "total_spend_usd": round(self.total_spend_usd, 6),
            "soft_cap_usd": self.soft_cap_usd,
            "hard_cap_usd": self.hard_cap_usd,
            "soft_cap_triggered": self.soft_cap_triggered,
            "hard_cap_triggered": self.hard_cap_triggered,
            "by_model_cell": dict(self.by_model_cell),
            "by_task_type": dict(self.by_task_type),
        }
