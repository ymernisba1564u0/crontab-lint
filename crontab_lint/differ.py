"""Compare two cron expressions and summarize their differences."""

from dataclasses import dataclass
from typing import List

from .parser import parse, ParseResult
from .explainer import explain


@dataclass
class DiffResult:
    expression_a: str
    expression_b: str
    valid_a: bool
    valid_b: bool
    explanation_a: str
    explanation_b: str
    field_diffs: List[str]
    summary: str


_FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]


def _field_diff(name: str, val_a: str, val_b: str) -> str | None:
    if val_a != val_b:
        return f"{name}: '{val_a}' -> '{val_b}'"
    return None


def diff(expression_a: str, expression_b: str) -> DiffResult:
    """Compare two cron expressions field-by-field."""
    result_a = parse(expression_a)
    result_b = parse(expression_b)

    valid_a = result_a.error is None
    valid_b = result_b.error is None

    explanation_a = explain(result_a) if valid_a else f"Invalid: {result_a.error}"
    explanation_b = explain(result_b) if valid_b else f"Invalid: {result_b.error}"

    field_diffs: List[str] = []

    if valid_a and valid_b:
        fields_a = [
            result_a.minute, result_a.hour,
            result_a.day_of_month, result_a.month, result_a.day_of_week,
        ]
        fields_b = [
            result_b.minute, result_b.hour,
            result_b.day_of_month, result_b.month, result_b.day_of_week,
        ]
        for name, fa, fb in zip(_FIELD_NAMES, fields_a, fields_b):
            diff_line = _field_diff(name, fa, fb)
            if diff_line:
                field_diffs.append(diff_line)

    if not valid_a and not valid_b:
        summary = "Both expressions are invalid."
    elif not valid_a:
        summary = "First expression is invalid."
    elif not valid_b:
        summary = "Second expression is invalid."
    elif not field_diffs:
        summary = "Expressions are equivalent."
    else:
        summary = f"{len(field_diffs)} field(s) differ."

    return DiffResult(
        expression_a=expression_a,
        expression_b=expression_b,
        valid_a=valid_a,
        valid_b=valid_b,
        explanation_a=explanation_a,
        explanation_b=explanation_b,
        field_diffs=field_diffs,
        summary=summary,
    )
