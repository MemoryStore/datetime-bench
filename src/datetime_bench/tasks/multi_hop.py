# AI-ANCHOR: datetime-bench tasks: multi-hop reasoning engine
"""Task Type 3: chained temporal reasoning problems."""

from __future__ import annotations

import random
from datetime import timedelta

from ..formats import build_datetime, describe_datetime, next_weekday, nth_weekday_of_month
from ..types import TaskScenario
from .base import FORMAT_KEYS, base_gold_map


TASK_TYPE = "multi_hop_reasoning"


def _template_one(rng: random.Random):
    year = rng.randint(2025, 2030)
    month = rng.randint(1, 12)
    weekday = rng.choice([0, 1, 2, 3, 4])
    occurrence = rng.choice([1, 2, 3])
    tz_name = rng.choice(["UTC", "America/New_York", "Europe/London", "Asia/Tokyo"])
    meeting_date = nth_weekday_of_month(year, month, weekday, occurrence)
    meeting = build_datetime(meeting_date.year, meeting_date.month, meeting_date.day, 10, 0, tz_name)
    hours_before = rng.choice([24, 48, 72, 96])
    gold = meeting - timedelta(hours=hours_before)
    names = ["first", "second", "third"]
    instruction = (
        f"Alice's meeting is on the {names[occurrence - 1]} {meeting.strftime('%A')} of "
        f"{meeting.strftime('%B %Y')} at 10:00 AM in timezone {tz_name}. Bob's deadline is exactly "
        f"{hours_before} hours before Alice's meeting. What is Bob's deadline? Output in {{FORMAT}}."
    )
    steps = [
        f"Find the {occurrence} {meeting.strftime('%A')} of {meeting.strftime('%B %Y')}",
        f"Set time to 10:00 in timezone {tz_name}",
        f"Subtract {hours_before} hours",
    ]
    return gold, instruction, steps


def _template_two(rng: random.Random):
    deploy = build_datetime(rng.randint(2025, 2030), rng.randint(1, 12), rng.randint(1, 20), 9, 0, "UTC")
    expiry_days = rng.choice([45, 60, 90, 120])
    reminder_days = rng.choice([3, 7, 14])
    expiry = deploy + timedelta(days=expiry_days)
    gold = expiry - timedelta(days=reminder_days)
    instruction = (
        f"A server was deployed on {describe_datetime(deploy)}. Its SSL certificate expires exactly "
        f"{expiry_days} days later. A renewal reminder should fire {reminder_days} days before expiry "
        f"at the same local time. When does the reminder fire? Output in {{FORMAT}}."
    )
    steps = [
        f"Add {expiry_days} days to deployment",
        f"Subtract {reminder_days} days for the reminder",
    ]
    return gold, instruction, steps


def _template_three(rng: random.Random):
    start = build_datetime(rng.randint(2025, 2030), rng.randint(1, 12), rng.randint(1, 21), 16, 30, "America/Los_Angeles")
    target_weekday = rng.choice([0, 2, 4])
    followup = next_weekday(start, target_weekday)
    extra_hours = rng.choice([6, 12, 18])
    gold = followup + timedelta(hours=extra_hours)
    instruction = (
        f"A maintenance window starts on {describe_datetime(start)}. The follow-up review happens on the next "
        f"{followup.strftime('%A')} at the same local time, and the final sign-off is {extra_hours} hours after the review. "
        f"When is the final sign-off? Output in {{FORMAT}}."
    )
    steps = [
        f"Find the next {followup.strftime('%A')} after the start datetime",
        "Keep the same local time",
        f"Add {extra_hours} hours",
    ]
    return gold, instruction, steps


def _template_four(rng: random.Random):
    kickoff = build_datetime(rng.randint(2025, 2030), rng.randint(1, 12), rng.randint(1, 20), 8, 15, "Asia/Tokyo")
    sprint_weeks = rng.choice([1, 2, 3])
    qa_days = rng.choice([2, 3, 5])
    demo = kickoff + timedelta(weeks=sprint_weeks)
    gold = demo - timedelta(days=qa_days)
    instruction = (
        f"A product kickoff happens on {describe_datetime(kickoff)}. The demo is scheduled exactly {sprint_weeks} weeks later, "
        f"and QA freeze begins {qa_days} days before the demo at the same local time. When does QA freeze begin? "
        f"Output in {{FORMAT}}."
    )
    steps = [
        f"Add {sprint_weeks} weeks for the demo",
        f"Subtract {qa_days} days for QA freeze",
    ]
    return gold, instruction, steps


TEMPLATES = (_template_one, _template_two, _template_three, _template_four)


def generate(n: int = 20, seed: int = 42) -> list[TaskScenario]:
    rng = random.Random(seed + 33)
    tasks: list[TaskScenario] = []
    for index in range(1, n + 1):
        template = TEMPLATES[(index - 1) % len(TEMPLATES)]
        gold, instruction, steps = template(rng)
        instruction_by_format = {
            format_key: instruction.replace("{FORMAT}", format_key.replace("_", " "))
            for format_key in FORMAT_KEYS
        }
        tasks.append(
            TaskScenario(
                task_id=f"multi_hop_{index:03d}",
                task_type=TASK_TYPE,
                gold_datetime=gold,
                instruction_by_format=instruction_by_format,
                gold_formatted_by_format=base_gold_map(gold),
                metadata={"reasoning_steps": steps},
            )
        )
    return tasks
