"""Lint multiple expressions and return per-expression results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from crontab_lint.validator import ValidationResult, validate


@dataclass
class LintResult:
    expression: str
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def lint_one(expression: str) -> LintResult:
    """Lint a single cron expression."""
    result: ValidationResult = validate(expression)
    return LintResult(
        expression=expression,
        valid=result.valid,
        errors=list(result.errors),
        warnings=list(result.warnings),
    )


def lint_many(expressions: List[str]) -> List[LintResult]:
    """Lint multiple cron expressions."""
    return [lint_one(expr) for expr in expressions]


def summary_counts(results: List[LintResult]) -> dict:
    """Return a dict with total, valid, invalid, warning counts."""
    total = len(results)
    valid = sum(1 for r in results if r.valid)
    warnings = sum(1 for r in results if r.warnings)
    return {
        "total": total,
        "valid": valid,
        "invalid": total - valid,
        "with_warnings": warnings,
    }
