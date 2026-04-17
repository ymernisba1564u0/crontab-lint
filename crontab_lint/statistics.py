"""Compute statistics over a collection of cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from collections import Counter
from typing import List

from crontab_lint.validator import validate


@dataclass
class StatisticsReport:
    total: int
    valid_count: int
    invalid_count: int
    warning_count: int
    most_common_minutes: List[tuple]
    most_common_hours: List[tuple]
    most_common_dow: List[tuple]
    error_messages: List[str] = field(default_factory=list)


def _top(counter: Counter, n: int = 3) -> List[tuple]:
    return counter.most_common(n)


def compute(expressions: List[str], top_n: int = 3) -> StatisticsReport:
    """Compute aggregate statistics for a list of cron expressions."""
    valid_count = 0
    invalid_count = 0
    warning_count = 0
    minutes: Counter = Counter()
    hours: Counter = Counter()
    dow: Counter = Counter()
    error_messages: List[str] = []

    for expr in expressions:
        result = validate(expr)
        if result.valid:
            valid_count += 1
            warning_count += len(result.warnings)
            pr = result.parse_result
            if pr:
                minutes[pr.minute] += 1
                hours[pr.hour] += 1
                dow[pr.day_of_week] += 1
        else:
            invalid_count += 1
            error_messages.extend(result.errors)

    return StatisticsReport(
        total=len(expressions),
        valid_count=valid_count,
        invalid_count=invalid_count,
        warning_count=warning_count,
        most_common_minutes=_top(minutes, top_n),
        most_common_hours=_top(hours, top_n),
        most_common_dow=_top(dow, top_n),
        error_messages=error_messages,
    )
