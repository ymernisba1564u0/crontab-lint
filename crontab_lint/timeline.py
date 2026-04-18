"""Generate a text-based timeline view of cron occurrences over a time window."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from crontab_lint.scheduler import next_occurrences, SchedulerError


@dataclass
class TimelineResult:
    expression: str
    timezone: str
    window_hours: int
    occurrences: List[datetime] = field(default_factory=list)
    error: str = ""

    @property
    def valid(self) -> bool:
        return not self.error


def build_timeline(expression: str, timezone: str = "UTC", window_hours: int = 24, count: int = 50) -> TimelineResult:
    """Return occurrences within *window_hours* from now."""
    try:
        occurrences = next_occurrences(expression, timezone=timezone, count=count)
    except SchedulerError as exc:
        return TimelineResult(expression=expression, timezone=timezone, window_hours=window_hours, error=str(exc))

    if not occurrences:
        return TimelineResult(expression=expression, timezone=timezone, window_hours=window_hours)

    cutoff = occurrences[0] + timedelta(hours=window_hours)
    windowed = [dt for dt in occurrences if dt <= cutoff]
    return TimelineResult(expression=expression, timezone=timezone, window_hours=window_hours, occurrences=windowed)


def format_timeline_text(result: TimelineResult) -> str:
    """Render a simple ASCII timeline."""
    if not result.valid:
        return f"Error: {result.error}"

    lines = [f"Timeline for '{result.expression}' (next {result.window_hours}h, tz={result.timezone})"]
    lines.append("-" * 60)

    if not result.occurrences:
        lines.append("  No occurrences in window.")
        return "\n".join(lines)

    start = result.occurrences[0]
    end = result.occurrences[-1]
    total_seconds = max((end - start).total_seconds(), 1)
    width = 50

    for dt in result.occurrences:
        offset = (dt - start).total_seconds()
        pos = int(offset / total_seconds * width)
        bar = " " * pos + "|"
        lines.append(f"  {dt.strftime('%Y-%m-%d %H:%M %Z')}  {bar}")

    lines.append("-" * 60)
    lines.append(f"  {len(result.occurrences)} occurrence(s) shown.")
    return "\n".join(lines)
