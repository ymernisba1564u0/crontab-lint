"""Expand a cron expression into all concrete (minute, hour, dom, month, dow) tuples it matches within one week."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .parser import parse, ParseResult


@dataclass
class ExpandResult:
    expression: str
    valid: bool
    errors: List[str]
    tuples: List[Tuple[int, int, int, int, int]]  # (minute, hour, dom, month, dow)


def _expand_field(raw: str, lo: int, hi: int) -> List[int]:
    """Return sorted list of integers matched by a single cron field token."""
    values: List[int] = []
    for part in raw.split(","):
        if part == "*":
            values.extend(range(lo, hi + 1))
        elif "/" in part:
            base, step_s = part.split("/", 1)
            step = int(step_s)
            start = lo if base == "*" else int(base.split("-")[0])
            end = hi if base == "*" else (int(base.split("-")[1]) if "-" in base else hi)
            values.extend(range(start, end + 1, step))
        elif "-" in part:
            a, b = part.split("-", 1)
            values.extend(range(int(a), int(b) + 1))
        else:
            values.append(int(part))
    return sorted(set(v for v in values if lo <= v <= hi))


def expand(expression: str) -> ExpandResult:
    """Expand *expression* into all (minute, hour, dom, month, dow) tuples.

    The expansion covers dom 1-31, month 1-12, dow 0-6 — callers should
    filter impossible calendar combinations (e.g. Feb 31) themselves.
    """
    result: ParseResult = parse(expression)
    if not result.valid:
        return ExpandResult(
            expression=expression,
            valid=False,
            errors=result.errors,
            tuples=[],
        )

    f = result.fields  # type: ignore[union-attr]
    minutes = _expand_field(f.minute, 0, 59)
    hours = _expand_field(f.hour, 0, 23)
    doms = _expand_field(f.dom, 1, 31)
    months = _expand_field(f.month, 1, 12)
    dows = _expand_field(f.dow, 0, 6)

    tuples: List[Tuple[int, int, int, int, int]] = [
        (mi, h, d, mo, dw)
        for mo in months
        for d in doms
        for dw in dows
        for h in hours
        for mi in minutes
    ]

    return ExpandResult(
        expression=expression,
        valid=True,
        errors=[],
        tuples=tuples,
    )
