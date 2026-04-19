"""Detect scheduling conflicts between multiple cron expressions."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Tuple
from .scheduler import next_occurrences, SchedulerError


@dataclass
class ConflictResult:
    expressions: List[str]
    conflicts: List[Tuple[str, str, str]]  # (expr_a, expr_b, iso_time)
    total_conflicts: int
    checked_occurrences: int


def find_conflicts(
    expressions: List[str],
    timezone: str = "UTC",
    count: int = 50,
) -> ConflictResult:
    """Find expressions that fire at the same time within the next *count* occurrences."""
    schedules: dict[str, List] = {}
    for expr in expressions:
        try:
            occ = next_occurrences(expr, timezone=timezone, count=count)
            schedules[expr] = [dt.replace(second=0, microsecond=0) for dt in occ]
        except SchedulerError:
            schedules[expr] = []

    conflicts: List[Tuple[str, str, str]] = []
    exprs = list(schedules.keys())
    for i in range(len(exprs)):
        for j in range(i + 1, len(exprs)):
            a, b = exprs[i], exprs[j]
            shared = set(schedules[a]) & set(schedules[b])
            for ts in sorted(shared):
                conflicts.append((a, b, ts.isoformat()))

    return ConflictResult(
        expressions=expressions,
        conflicts=conflicts,
        total_conflicts=len(conflicts),
        checked_occurrences=count,
    )
