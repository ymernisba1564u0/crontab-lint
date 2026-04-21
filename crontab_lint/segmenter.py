"""Segment a cron expression into labeled time buckets."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import parse, ParseResult


@dataclass
class SegmentResult:
    expression: str
    valid: bool
    errors: List[str]
    segments: List[dict]  # [{"field": str, "raw": str, "type": str}]


_FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]

_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}


def _classify(raw: str) -> str:
    """Return a short type label for a cron field value."""
    if raw == "*":
        return "wildcard"
    if "/" in raw:
        return "step"
    if "," in raw:
        return "list"
    if "-" in raw:
        return "range"
    return "literal"


def segment(expression: str) -> SegmentResult:
    """Parse *expression* and return a labelled segment for every field.

    For invalid expressions the ``segments`` list is empty and ``errors``
    contains the parser error messages.
    """
    result: ParseResult = parse(expression)

    if not result.valid:
        return SegmentResult(
            expression=expression,
            valid=False,
            errors=result.errors,
            segments=[],
        )

    parts = expression.split()
    segments: List[dict] = []
    for name, raw in zip(_FIELD_NAMES, parts):
        lo, hi = _RANGES[name]
        segments.append(
            {
                "field": name,
                "raw": raw,
                "type": _classify(raw),
                "range": {"min": lo, "max": hi},
            }
        )

    return SegmentResult(
        expression=expression,
        valid=True,
        errors=[],
        segments=segments,
    )
