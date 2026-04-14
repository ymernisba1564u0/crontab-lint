"""Orchestrates parsing, explaining, scheduling and formatting into a LintReport."""

from datetime import datetime
from typing import List, Optional

from crontab_lint.formatter import LintReport
from crontab_lint.parser import parse
from crontab_lint.explainer import explain
from crontab_lint.scheduler import next_occurrences, SchedulerError


def build_report(
    expression: str,
    timezone: str = "UTC",
    count: int = 5,
    now: Optional[datetime] = None,
) -> LintReport:
    """Parse the expression and build a complete LintReport.

    Args:
        expression: A cron expression string (5 fields).
        timezone: IANA timezone name, e.g. "America/New_York".
        count: Number of upcoming occurrences to compute.
        now: Reference datetime for scheduling (defaults to current time).

    Returns:
        A populated LintReport instance.
    """
    result = parse(expression)

    if not result.valid:
        return LintReport(
            expression=expression,
            timezone=timezone,
            is_valid=False,
            explanation=None,
            errors=result.errors,
            next_occurrences=[],
        )

    explanation = explain(result)

    occurrences: List[datetime] = []
    errors = []
    try:
        occurrences = next_occurrences(
            result, tz=timezone, count=count, now=now
        )
    except SchedulerError as exc:
        errors.append(str(exc))

    return LintReport(
        expression=expression,
        timezone=timezone,
        is_valid=not errors,
        explanation=explanation,
        errors=errors,
        next_occurrences=occurrences,
    )
