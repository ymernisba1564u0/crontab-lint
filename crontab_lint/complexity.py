"""Score the complexity of a cron expression."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from .parser import parse, ParseResult


@dataclass
class ComplexityResult:
    expression: str
    score: int
    level: str  # simple | moderate | complex
    reasons: List[str]
    valid: bool


def _field_complexity(value: str) -> tuple[int, list[str]]:
    """Return (score, reasons) for a single field token."""
    score = 0
    reasons: list[str] = []

    if value == "*":
        return 0, []

    if "," in value:
        count = value.count(",") + 1
        score += count
        reasons.append(f"list with {count} items")

    if "/" in value:
        score += 2
        reasons.append("step value")

    if "-" in value.lstrip("-"):
        score += 1
        reasons.append("range")

    if value != "*" and "," not in value and "/" not in value and "-" not in value:
        score += 1  # specific value

    return score, reasons


def _level(score: int) -> str:
    if score <= 2:
        return "simple"
    if score <= 6:
        return "moderate"
    return "complex"


def complexity(expression: str) -> ComplexityResult:
    result = parse(expression)
    if not result.valid:
        return ComplexityResult(
            expression=expression,
            score=-1,
            level="unknown",
            reasons=[result.error or "invalid expression"],
            valid=False,
        )

    fields = [result.minute, result.hour, result.day, result.month, result.dow]
    total = 0
    all_reasons: list[str] = []
    names = ["minute", "hour", "day", "month", "dow"]

    for name, field in zip(names, fields):
        s, reasons = _field_complexity(field)
        total += s
        for r in reasons:
            all_reasons.append(f"{name}: {r}")

    return ComplexityResult(
        expression=expression,
        score=total,
        level=_level(total),
        reasons=all_reasons,
        valid=True,
    )
