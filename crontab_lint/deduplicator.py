"""Deduplicator: find and remove duplicate cron expressions from a list."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .normalizer import normalize


@dataclass
class DeduplicateResult:
    """Result of a deduplication pass over a list of cron expressions."""

    original: List[str]
    unique: List[str]
    duplicates: List[Tuple[str, str]]  # (duplicate_expr, canonical_expr)
    duplicate_count: int
    unique_count: int


def _canonical(expression: str) -> str:
    """Return the normalised form of *expression* for identity comparison."""
    result = normalize(expression)
    # If normalisation failed (invalid expression) fall back to the raw value
    return result.normalized if result.normalized else expression


def deduplicate(expressions: List[str]) -> DeduplicateResult:
    """Deduplicate *expressions*, treating alias-equivalent entries as equal.

    The *first* occurrence of each canonical form is kept.  Later occurrences
    are recorded as duplicates together with the canonical expression they
    match.

    Args:
        expressions: Ordered list of raw cron expression strings.

    Returns:
        A :class:`DeduplicateResult` describing the outcome.
    """
    seen: dict[str, str] = {}  # canonical -> first raw expression
    unique: List[str] = []
    duplicates: List[Tuple[str, str]] = []

    for expr in expressions:
        canon = _canonical(expr)
        if canon in seen:
            duplicates.append((expr, seen[canon]))
        else:
            seen[canon] = expr
            unique.append(expr)

    return DeduplicateResult(
        original=list(expressions),
        unique=unique,
        duplicates=duplicates,
        duplicate_count=len(duplicates),
        unique_count=len(unique),
    )
