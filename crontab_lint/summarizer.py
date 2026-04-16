"""Summarize a collection of cron expressions into statistics."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .validator import validate


@dataclass
class SummaryReport:
    total: int
    valid: int
    invalid: int
    warning_count: int
    invalid_expressions: List[str] = field(default_factory=list)
    warning_expressions: List[str] = field(default_factory=list)

    @property
    def valid_pct(self) -> float:
        return round(100 * self.valid / self.total, 1) if self.total else 0.0


def summarize(expressions: List[str]) -> SummaryReport:
    """Validate each expression and aggregate results."""
    total = len(expressions)
    valid = 0
    invalid = 0
    warning_count = 0
    invalid_expressions: List[str] = []
    warning_expressions: List[str] = []

    for expr in expressions:
        result = validate(expr)
        if result.is_valid:
            valid += 1
            if result.warnings:
                warning_count += len(result.warnings)
                warning_expressions.append(expr)
        else:
            invalid += 1
            invalid_expressions.append(expr)

    return SummaryReport(
        total=total,
        valid=valid,
        invalid=invalid,
        warning_count=warning_count,
        invalid_expressions=invalid_expressions,
        warning_expressions=warning_expressions,
    )
