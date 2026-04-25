"""Detect overlapping (redundant) cron expressions in a set."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .scheduler import next_occurrences, SchedulerError

_SAMPLE_COUNT = 60  # occurrences to sample per expression
_DEFAULT_TZ = "UTC"


@dataclass
class OverlapResult:
    expressions: List[str]
    timezone: str
    overlaps: List[Tuple[str, str, int]]  # (expr_a, expr_b, shared_count)
    total_pairs_checked: int


def _occurrence_set(expr: str, tz: str) -> set[str]:
    """Return a set of ISO timestamp strings for the next N occurrences."""
    try:
        occ = next_occurrences(expr, count=_SAMPLE_COUNT, timezone=tz)
        return {dt.isoformat() for dt in occ}
    except SchedulerError:
        return set()


def find_overlaps(
    expressions: List[str],
    timezone: str = _DEFAULT_TZ,
    threshold: int = 1,
) -> OverlapResult:
    """Find pairs of expressions whose scheduled times overlap.

    Two expressions *overlap* when they share at least *threshold* occurrences
    in the sampled window.  A threshold of 1 (default) flags any shared run.
    """
    sets: dict[str, set[str]] = {
        expr: _occurrence_set(expr, timezone) for expr in expressions
    }

    overlaps: List[Tuple[str, str, int]] = []
    pairs_checked = 0
    exprs = list(expressions)

    for i in range(len(exprs)):
        for j in range(i + 1, len(exprs)):
            a, b = exprs[i], exprs[j]
            shared = sets[a] & sets[b]
            pairs_checked += 1
            if len(shared) >= threshold:
                overlaps.append((a, b, len(shared)))

    return OverlapResult(
        expressions=exprs,
        timezone=timezone,
        overlaps=overlaps,
        total_pairs_checked=pairs_checked,
    )
