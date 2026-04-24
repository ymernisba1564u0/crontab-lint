"""Compute estimated run frequency for cron expressions."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .parser import parse, ParseResult


@dataclass
class FrequencyResult:
    expression: str
    valid: bool
    errors: list[str]
    runs_per_hour: Optional[float]
    runs_per_day: Optional[float]
    runs_per_week: Optional[float]
    runs_per_month: Optional[float]
    label: Optional[str]


_MINUTES_IN_HOUR = 60
_MINUTES_IN_DAY = 1440
_MINUTES_IN_WEEK = 10080
_MINUTES_IN_MONTH = 43200  # 30-day approximation


def _count_values(field: str, min_val: int, max_val: int) -> int:
    """Count distinct values matched by a cron field token."""
    if field == "*":
        return max_val - min_val + 1
    total = 0
    for part in field.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            lo, hi = (min_val, max_val) if base == "*" else map(int, base.split("-"))
            total += len(range(lo, hi + 1, step))
        elif "-" in part:
            lo, hi = map(int, part.split("-", 1))
            total += hi - lo + 1
        else:
            total += 1
    return total


def _label(runs_per_day: float) -> str:
    if runs_per_day >= _MINUTES_IN_DAY:
        return "every minute"
    if runs_per_day >= 60:
        return "every hour or more"
    if runs_per_day >= 2:
        return "multiple times a day"
    if runs_per_day >= 1:
        return "daily"
    if runs_per_day >= 1 / 7:
        return "weekly"
    return "monthly or less"


def frequency(expression: str) -> FrequencyResult:
    """Return estimated run frequency for *expression*."""
    result = parse(expression)
    if not result.valid:
        return FrequencyResult(
            expression=expression,
            valid=False,
            errors=result.errors,
            runs_per_hour=None,
            runs_per_day=None,
            runs_per_week=None,
            runs_per_month=None,
            label=None,
        )

    f = result.fields
    minutes = _count_values(f.minute, 0, 59)
    hours = _count_values(f.hour, 0, 23)
    doms = _count_values(f.day_of_month, 1, 31)
    months = _count_values(f.month, 1, 12)
    dows = _count_values(f.day_of_week, 0, 6)

    # Runs per month: minutes * hours * min(doms, effective days from dow) * months/12
    effective_days = min(doms, dows * 4)  # rough weekly-to-monthly mapping
    runs_per_month = minutes * hours * effective_days * (months / 12)
    runs_per_week = runs_per_month / 4.0
    runs_per_day = runs_per_week / 7.0
    runs_per_hour = runs_per_day / 24.0

    return FrequencyResult(
        expression=expression,
        valid=True,
        errors=[],
        runs_per_hour=round(runs_per_hour, 4),
        runs_per_day=round(runs_per_day, 4),
        runs_per_week=round(runs_per_week, 4),
        runs_per_month=round(runs_per_month, 4),
        label=_label(runs_per_day),
    )
