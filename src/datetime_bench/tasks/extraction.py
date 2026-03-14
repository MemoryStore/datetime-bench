# AI-ANCHOR: datetime-bench tasks: passage extraction cases
"""Task Type 5: extract a relevant datetime from a short passage."""

from __future__ import annotations

import random

from ..formats import describe_datetime, random_datetime
from ..types import TaskScenario
from .base import FORMAT_KEYS, base_gold_map


TASK_TYPE = "extraction_from_passage"

NAMES = ["Avery", "Jordan", "Priya", "Marco", "Elena", "Samir", "Naomi", "Lena"]
DEPARTMENTS = ["Finance", "Operations", "Product", "Security", "Marketing", "Research"]
TOPICS = ["budget planning", "risk review", "model rollout", "incident drills", "forecasting", "compliance"]
EVENT_TYPES = ["meeting", "review", "deadline", "launch", "briefing"]


def generate(n: int = 20, seed: int = 42) -> list[TaskScenario]:
    rng = random.Random(seed + 55)
    tasks: list[TaskScenario] = []
    for index in range(1, n + 1):
        gold = random_datetime(rng)
        distractor = random_datetime(rng)
        while distractor.date() == gold.date() and distractor.timetz() == gold.timetz():
            distractor = random_datetime(rng)
        name = rng.choice(NAMES)
        department = rng.choice(DEPARTMENTS)
        event_type = rng.choice(EVENT_TYPES)
        topic_one = rng.choice(TOPICS)
        topic_two = rng.choice([item for item in TOPICS if item != topic_one])
        gold_text = describe_datetime(gold)
        distractor_text = describe_datetime(distractor)
        passage = (
            f"{name}, the VP of {department}, circulated a note to 17 attendees about the upcoming {event_type}. "
            f"The final agenda was locked on {gold_text}. A separate travel hold remains in place until {distractor_text}. "
            f"The discussion will cover {topic_one} and {topic_two}, and room 204 has already been reserved."
        )
        instruction_by_format = {
            format_key: (
                f"Read the following passage and extract the {event_type} date. Output in "
                f"{format_key.replace('_', ' ')}.\n\n{passage}"
            )
            for format_key in FORMAT_KEYS
        }
        tasks.append(
            TaskScenario(
                task_id=f"extract_{index:03d}",
                task_type=TASK_TYPE,
                gold_datetime=gold,
                instruction_by_format=instruction_by_format,
                gold_formatted_by_format=base_gold_map(gold),
                metadata={"event_type": event_type, "passage": passage},
            )
        )
    return tasks
