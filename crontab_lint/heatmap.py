"""Generate a frequency heatmap for a cron expression over a time window."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Dict, List

from crontab_lint.scheduler import next_occurrences


@dataclass
class HeatmapResult:
    expression: str
    timezone: str
    hours: Dict[int, int] = field(default_factory=dict)   # hour -> count
    weekdays: Dict[int, int] = field(default_factory=dict)  # 0=Mon -> count
    months: Dict[int, int] = field(default_factory=dict)  # 1-12 -> count
    total: int = 0


DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
MONTH_NAMES = ["", "Jan", "Feb", "Mar", "Apr", "May", "Jun",
               "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ndef build_heatmap(
    expression: str,
 "UTC",
    days = 30,
    count: int = 1,
) -> HeatmapResult:
    """ occurrences and bucket them by hour, weekday, andurrences = next_occurrences(expression, timezone=timezone, count=count)
    result = HeatmapResult(expression=expression, timezone=timezone)

    for dt in occurrences:
        h = dt.hour
        wd = dt.weekday()  # 0=Monday
        m = dt.month
        result.hours[h] = result.hours.get(h, 0) + 1
        result.weekdays[wd] = result.weekdays.get(wd, 0) + 1
        result.months[m] = result.months.get(m, 0) + 1
        result.total += 1

    return result


def _bar(count: int, max_count: int, width: int = 20) -> str:
    if max_count == 0:
        return ""
    filled = round(count / max_count * width)
    return "█" * filled + "░" * (width - filled)


def format_heatmap_text(result: HeatmapResult) -> str:
    lines: List[str] = []
    lines.append(f"Heatmap for: {result.expression}  [{result.timezone}]  total={result.total}")

    lines.append("\nBy Hour:")
    max_h = max(result.hours.values(), default=1)
    for h in range(24):
        c = result.hours.get(h, 0)
        lines.append(f"  {h:02d}:00  {_bar(c, max_h)} {c}")

    lines.append("\nBy Weekday:")
    max_w = max(result.weekdays.values(), default=1)
    for wd in range(7):
        c = result.weekdays.get(wd, 0)
        lines.append(f"  {DAY_NAMES[wd]}  {_bar(c, max_w)} {c}")

    lines.append("\nBy Month:")
    max_m = max(result.months.values(), default=1)
    for m in range(1, 13):
        c = result.months.get(m, 0)
        lines.append(f"  {MONTH_NAMES[m]}  {_bar(c, max_m)} {c}")

    return "\n".join(lines)
