"""High-level validation facade that combines parsing and semantic checks."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseResult


@dataclass
class ValidationResult:
    expression: str
    is_valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    parse_result: Optional[ParseResult] = None


_SUSPICIOUS_PATTERNS = [
    ("* * * * *", "Expression runs every minute — ensure this is intentional."),
    ("* * * * 0", "Runs every minute on Sundays — did you mean '0 * * * 0'?"),
    ("0 0 31 * *", "Day 31 does not exist in all months; some runs will be skipped."),
    ("0 0 30 2 *", "February never has 30 days; this expression will never run."),
    ("0 0 29 2 *", "Feb 29 only exists in leap years; runs will be infrequent."),
]


def _check_warnings(expression: str) -> List[str]:
    """Return advisory warnings for known suspicious patterns."""
    warnings: List[str] = []
    normalised = " ".join(expression.split())
    for pattern, message in _SUSPICIOUS_PATTERNS:
        if normalised == pattern:
            warnings.append(message)
    return warnings


def validate(expression: str) -> ValidationResult:
    """Parse *expression* and return a :class:`ValidationResult`.

    Errors come from the parser; warnings are heuristic advisories.
    """
    result = parse(expression)
    if not result.is_valid:
        return ValidationResult(
            expression=expression,
            is_valid=False,
            errors=list(result.errors),
            parse_result=result,
        )

    warnings = _check_warnings(expression)
    return ValidationResult(
        expression=expression,
        is_valid=True,
        warnings=warnings,
        parse_result=result,
    )
