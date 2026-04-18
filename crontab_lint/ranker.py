"""Rank cron expressions by estimated execution frequency."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from crontab_lint.parser import parse, ParseResult


@dataclass
class RankResult:
    expression: str
    valid: bool
    frequency_score: float  # estimated runs per day; -1 if invalid
    rank: int


def _field_weight(raw: str, total: int) -> float:
    """Return fraction of slots matched (0-1)."""
    if raw == "*":
        return 1.0
    if "," in raw:
        return len(raw.split(",")) / total
    if "-" in raw and "/" not in raw:
        lo, hi = raw.split("-", 1)
        try:
            return (int(hi) - int(lo) + 1) / total
        except ValueError:
            return 1.0
    if raw.startswith("*/"):
        try:
            step = int(raw[2:])
            return 1.0 / step
        except ValueError:
            return 1.0
    if "/" in raw:
        # range/step
        _, step = raw.rsplit("/", 1)
        try:
            return 1.0 / int(step)
        except ValueError:
            return 1.0
    return 1.0 / total


def _frequency_score(pr: ParseResult) -> float:
    """Estimate runs per day."""
    minutes_per_day = 1440.0
    minute_w = _field_weight(pr.minute.raw, 60)
    hour_w = _field_weight(pr.hour.raw, 24)
    dom_w = _field_weight(pr.dom.raw, 31)
    month_w = _field_weight(pr.month.raw, 12)
    # runs per day ≈ minute_w * hour_w * dom_w * month_w * 1440
    return round(minutes_per_day * minute_w * hour_w * dom_w * month_w, 4)


def rank(expressions: List[str]) -> List[RankResult]:
    """Rank expressions from most to least frequent."""
    results: List[RankResult] = []
    for expr in expressions:
        pr = parse(expr)
        if pr is None:
            results.append(RankResult(expression=expr, valid=False, frequency_score=-1.0, rank=0))
        else:
            score = _frequency_score(pr)
            results.append(RankResult(expression=expr, valid=True, frequency_score=score, rank=0))

    valid = sorted([r for r in results if r.valid], key=lambda r: r.frequency_score, reverse=True)
    invalid = [r for r in results if not r.valid]

    for i, r in enumerate(valid, start=1):
        r.rank = i
    for i, r in enumerate(invalid, start=len(valid) + 1):
        r.rank = i

    ordered = {r.expression: r for r in valid}
    ordered.update({r.expression: r for r in invalid})
    return [ordered[e] for e in expressions]
