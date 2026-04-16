"""Compare two cron expressions and report semantic equivalence."""
from dataclasses import dataclass, field
from typing import List
from .validator import validate
from .normalizer import normalize


@dataclass
class CompareResult:
    expression_a: str
    expression_b: str
    normalized_a: str
    normalized_b: str
    are_equivalent: bool
    both_valid: bool
    errors_a: List[str] = field(default_factory=list)
    errors_b: List[str] = field(default_factory=list)


def compare(expr_a: str, expr_b: str) -> CompareResult:
    """Semantically compare two cron expressions after normalization."""
    val_a = validate(expr_a)
    val_b = validate(expr_b)

    both_valid = val_a.is_valid and val_b.is_valid

    if not both_valid:
        return CompareResult(
            expression_a=expr_a,
            expression_b=expr_b,
            normalized_a=expr_a,
            normalized_b=expr_b,
            are_equivalent=False,
            both_valid=False,
            errors_a=val_a.errors,
            errors_b=val_b.errors,
        )

    norm_a = normalize(expr_a)
    norm_b = normalize(expr_b)

    return CompareResult(
        expression_a=expr_a,
        expression_b=expr_b,
        normalized_a=norm_a.normalized,
        normalized_b=norm_b.normalized,
        are_equivalent=norm_a.normalized == norm_b.normalized,
        both_valid=True,
        errors_a=[],
        errors_b=[],
    )
