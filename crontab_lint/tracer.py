"""Trace cron expression execution history backwards from a reference point."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import List

from .scheduler import _get_timezone, _matches_field, SchedulerError
from .validator import validate


@dataclass
class TraceResult:
    expression: str
    timezone: str
    count: int
    valid: bool
    errors: List[str]
    occurrences: List[datetime] = field(default_factory=list)


def _matches_cron(dt: datetime, fields) -> bool:
    """Return True if *dt* matches all five cron fields."""
    return (
        _matches_field(dt.minute, fields.minute)
        and _matches_field(dt.hour, fields.hour)
        and _matches_field(dt.day, fields.dom)
        and _matches_field(dt.month, fields.month)
        and _matches_field(dt.weekday() + 1 if dt.weekday() < 6 else 0, fields.dow)
    )


def trace(
    expression: str,
    tz_name: str = "UTC",
    count: int = 5,
    before: datetime | None = None,
) -> TraceResult:
    """Return the *count* most-recent past occurrences before *before*.

    Parameters
    ----------
    expression:
        A five-field cron expression.
    tz_name:
        IANA timezone name used to interpret the schedule.
    count:
        Number of past occurrences to return (1-100).
    before:
        Upper bound (exclusive).  Defaults to *now* in *tz_name*.
    """
    count = max(1, min(count, 100))

    result = validate(expression)
    if not result.valid:
        return TraceResult(
            expression=expression,
            timezone=tz_name,
            count=count,
            valid=False,
            errors=result.errors,
        )

    try:
        tz = _get_timezone(tz_name)
    except SchedulerError as exc:
        return TraceResult(
            expression=expression,
            timezone=tz_name,
            count=count,
            valid=False,
            errors=[str(exc)],
        )

    if before is None:
        before = datetime.now(tz=timezone.utc).astimezone(tz)
    elif before.tzinfo is None:
        before = before.replace(tzinfo=tz)

    # Walk backwards minute-by-minute from (before - 1 min)
    fields = result.parse_result
    cursor = before.replace(second=0, microsecond=0) - timedelta(minutes=1)
    occurrences: List[datetime] = []
    max_steps = 60 * 24 * 366  # safety cap ~1 year

    for _ in range(max_steps):
        if len(occurrences) >= count:
            break
        if _matches_cron(cursor, fields):
            occurrences.append(cursor.astimezone(tz))
        cursor -= timedelta(minutes=1)

    return TraceResult(
        expression=expression,
        timezone=tz_name,
        count=count,
        valid=True,
        errors=[],
        occurrences=occurrences,
    )
