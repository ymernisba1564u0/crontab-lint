"""Builds a :class:`~crontab_lint.formatter.LintReport` from an expression."""

from typing import List, Optional

from .formatter import LintReport
from .validator import validate
from .explainer import explain
from .scheduler import next_occurrences, SchedulerError


def build_report(
    expression: str,
    timezone: str = "UTC",
    count: int = 5,
) -> LintReport:
    """Validate *expression*, explain it, and compute upcoming occurrences.

    Parameters
    ----------
    expression:
        A five-field cron expression string.
    timezone:
        IANA timezone name used for scheduling previews.
    count:
        Number of upcoming occurrences to include in the report.

    Returns
    -------
    LintReport
        Populated report ready for formatting.
    """
    validation = validate(expression)

    human_readable: Optional[str] = None
    occurrences: List = []
    errors: List[str] = list(validation.errors)
    warnings: List[str] = list(validation.warnings)

    if validation.is_valid:
        human_readable = explain(expression)
        try:
            occurrences = next_occurrences(expression, timezone=timezone, count=count)
        except SchedulerError as exc:
            errors.append(str(exc))

    return LintReport(
        expression=expression,
        is_valid=validation.is_valid,
        errors=errors,
        warnings=warnings,
        human_readable=human_readable,
        next_occurrences=occurrences,
        timezone=timezone,
    )
