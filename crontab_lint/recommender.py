"""Recommender module for crontab-lint.

Suggests simpler or more idiomatic cron expressions that are equivalent
(or nearly equivalent) to the given input, based on common patterns.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseResult
from .validator import validate


@dataclass
class Suggestion:
    """A single recommendation for an alternative cron expression."""

    expression: str
    reason: str
    confidence: float  # 0.0 – 1.0


@dataclass
class RecommendResult:
    """Result returned by :func:`recommend`."""

    original: str
    valid: bool
    errors: List[str]
    suggestions: List[Suggestion] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

_SPECIAL_ALIASES: dict[str, str] = {
    "* * * * *": "@every_minute — use @reboot or ensure this is intentional",
    "0 * * * *": "@hourly",
    "0 0 * * *": "@daily",
    "0 0 * * 0": "@weekly",
    "0 0 1 * *": "@monthly",
    "0 0 1 1 *": "@yearly",
}


def _fields(expr: str) -> List[str]:
    """Split a normalised expression into its five fields."""
    return expr.strip().split()


def _suggest_special_alias(expr: str) -> Optional[Suggestion]:
    """Return a @-alias suggestion when the expression matches a well-known pattern."""
    hint = _SPECIAL_ALIASES.get(expr)
    if hint:
        # Only offer the alias as a suggestion, not a replacement, so the
        # original numeric form (which is universally supported) is preserved.
        return Suggestion(
            expression=expr,
            reason=f"This expression is equivalent to the special alias {hint}.",
            confidence=1.0,
        )
    return None


def _suggest_wildcard_step_simplification(parts: List[str]) -> List[Suggestion]:
    """Suggest removing redundant */1 steps (equivalent to plain '*')."""
    suggestions: List[Suggestion] = []
    simplified = list(parts)
    changed = False
    for i, p in enumerate(parts):
        if p == "*/1":
            simplified[i] = "*"
            changed = True
    if changed:
        new_expr = " ".join(simplified)
        suggestions.append(
            Suggestion(
                expression=new_expr,
                reason="'*/1' is identical to '*'; simplify to '*'.",
                confidence=1.0,
            )
        )
    return suggestions


def _suggest_redundant_range(parts: List[str]) -> List[Suggestion]:
    """Suggest replacing a full-range value (e.g. 0-59) with '*'."""
    _field_ranges = [
        (0, 59),   # minute
        (0, 23),   # hour
        (1, 31),   # day-of-month
        (1, 12),   # month
        (0, 6),    # day-of-week
    ]
    suggestions: List[Suggestion] = []
    simplified = list(parts)
    changed = False
    for i, (p, (lo, hi)) in enumerate(zip(parts, _field_ranges)):
        if "-" in p and "/" not in p:
            try:
                a, b = p.split("-", 1)
                if int(a) == lo and int(b) == hi:
                    simplified[i] = "*"
                    changed = True
            except ValueError:
                pass
    if changed:
        new_expr = " ".join(simplified)
        suggestions.append(
            Suggestion(
                expression=new_expr,
                reason="A range that covers the full allowed span can be replaced with '*'.",
                confidence=0.95,
            )
        )
    return suggestions


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def recommend(expression: str) -> RecommendResult:
    """Analyse *expression* and return improvement suggestions.

    Parameters
    ----------
    expression:
        A standard five-field cron expression.

    Returns
    -------
    RecommendResult
        Contains the original expression, validity flag, any parse errors,
        and a list of :class:`Suggestion` objects ordered by confidence
        (highest first).
    """
    result = validate(expression)
    if not result.valid:
        return RecommendResult(
            original=expression,
            valid=False,
            errors=result.errors,
            suggestions=[],
        )

    parts = _fields(expression)
    suggestions: List[Suggestion] = []

    alias_hint = _suggest_special_alias(expression)
    if alias_hint:
        suggestions.append(alias_hint)

    suggestions.extend(_suggest_wildcard_step_simplification(parts))
    suggestions.extend(_suggest_redundant_range(parts))

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique: List[Suggestion] = []
    for s in sorted(suggestions, key=lambda x: -x.confidence):
        if s.expression not in seen or s.reason not in [u.reason for u in unique]:
            seen.add(s.expression)
            unique.append(s)

    return RecommendResult(
        original=expression,
        valid=True,
        errors=[],
        suggestions=unique,
    )
