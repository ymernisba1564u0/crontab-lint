"""Timezone-aware scheduling preview for cron expressions."""

from datetime import datetime, timedelta
from typing import Iterator, List, Optional

try:
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
except ImportError:
    from backports.zoneinfo import ZoneInfo, ZoneInfoNotFoundError  # type: ignore

from crontab_lint.parser import ParseResult, parse


class SchedulerError(Exception):
    """Raised when scheduling preview cannot be generated."""


def _get_timezone(tz_name: str) -> ZoneInfo:
    """Resolve a timezone by name, raising SchedulerError on failure."""
    try:
        return ZoneInfo(tz_name)
    except (ZoneInfoNotFoundError, KeyError):
        raise SchedulerError(f"Unknown timezone: '{tz_name}'")


def _matches_field(value: int, field_expr: str, min_val: int, max_val: int) -> bool:
    """Return True if *value* satisfies *field_expr*."""
    if field_expr == "*":
        return True
    for part in field_expr.split(","):
        if "/" in part:
            base, step = part.split("/", 1)
            step = int(step)
            start = min_val if base == "*" else int(base.split("-")[0])
            end = max_val if base == "*" or "-" not in base else int(base.split("-")[1])
            if start <= value <= end and (value - start) % step == 0:
                return True
        elif "-" in part:
            lo, hi = part.split("-", 1)
            if int(lo) <= value <= int(hi):
                return True
        else:
            if value == int(part):
                return True
    return False


def next_occurrences(
    expression: str,
    count: int = 5,
    tz_name: str = "UTC",
    after: Optional[datetime] = None,
) -> List[datetime]:
    """Return the next *count* scheduled datetimes for *expression*.

    Args:
        expression: A standard 5-field cron expression.
        count: Number of upcoming occurrences to return.
        tz_name: IANA timezone name (e.g. ``"America/New_York"``).
        after: Start searching after this datetime (defaults to now).

    Returns:
        A list of timezone-aware :class:`datetime` objects.
    """
    result: ParseResult = parse(expression)
    if not result.valid:
        raise SchedulerError(f"Invalid cron expression: {result.error}")

    tz = _get_timezone(tz_name)
    minute_expr, hour_expr, dom_expr, month_expr, dow_expr = [
        f.raw for f in result.fields
    ]

    current = (after or datetime.now(tz=tz)).replace(second=0, microsecond=0)
    current += timedelta(minutes=1)  # start from the next minute

    occurrences: List[datetime] = []
    # Guard against infinite loops — search at most 4 years ahead
    limit = current + timedelta(days=366 * 4)

    while len(occurrences) < count and current < limit:
        if not _matches_field(current.month, month_expr, 1, 12):
            current += timedelta(hours=1)
            current = current.replace(minute=0)
            continue
        if not _matches_field(current.day, dom_expr, 1, 31):
            current += timedelta(days=1)
            current = current.replace(hour=0, minute=0)
            continue
        if not _matches_field(current.weekday() + 1 if current.weekday() < 6 else 0, dow_expr, 0, 7):
            current += timedelta(days=1)
            current = current.replace(hour=0, minute=0)
            continue
        if not _matches_field(current.hour, hour_expr, 0, 23):
            current += timedelta(hours=1)
            current = current.replace(minute=0)
            continue
        if not _matches_field(current.minute, minute_expr, 0, 59):
            current += timedelta(minutes=1)
            continue
        occurrences.append(current)
        current += timedelta(minutes=1)

    return occurrences
