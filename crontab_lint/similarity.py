"""Compute similarity score between two cron expressions."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Optional
from crontab_lint.parser import parse, ParseResult

FIELD_NAMES = ("minute", "hour", "day", "month", "dow")


@dataclass
class SimilarityResult:
    expression_a: str
    expression_b: str
    score: float  # 0.0 – 1.0
    matching_fields: int
    total_fields: int
    both_valid: bool
    error: Optional[str] = None


def _field_score(a: str, b: str) -> float:
    """Return 1.0 if fields are identical, 0.5 if one is wildcard, else 0.0."""
    if a == b:
        return 1.0
    if a == "*" or b == "*":
        return 0.5
    return 0.0


def similarity(expr_a: str, expr_b: str) -> SimilarityResult:
    pa: ParseResult = parse(expr_a)
    pb: ParseResult = parse(expr_b)

    both_valid = pa.valid and pb.valid

    if not both_valid:
        err = pa.error if not pa.valid else pb.error
        return SimilarityResult(
            expression_a=expr_a,
            expression_b=expr_b,
            score=0.0,
            matching_fields=0,
            total_fields=5,
            both_valid=False,
            error=err,
        )

    fields_a = (
        pa.fields.minute,
        pa.fields.hour,
        pa.fields.day,
        pa.fields.month,
        pa.fields.dow,
    )
    fields_b = (
        pb.fields.minute,
        pb.fields.hour,
        pb.fields.day,
        pb.fields.month,
        pb.fields.dow,
    )

    scores = [_field_score(a, b) for a, b in zip(fields_a, fields_b)]
    matching = sum(1 for s in scores if s == 1.0)
    total = len(scores)
    score = round(sum(scores) / total, 4)

    return SimilarityResult(
        expression_a=expr_a,
        expression_b=expr_b,
        score=score,
        matching_fields=matching,
        total_fields=total,
        both_valid=True,
    )
