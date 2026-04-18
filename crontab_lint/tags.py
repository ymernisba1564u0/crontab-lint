"""Tag/categorize cron expressions by their schedule pattern."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from crontab_lint.parser import ParseResult


@dataclass
class TagResult:
    expression: str
    tags: List[str] = field(default_factory=list)
    valid: bool = True


_KNOWN_TAGS = [
    ("every_minute", lambda p: p.minute == "*" and p.hour == "*"),
    ("hourly",       lambda p: p.minute != "*" and p.hour == "*"),
    ("daily",        lambda p: p.hour != "*" and p.day_of_month == "*" and p.day_of_week == "*"),
    ("weekly",       lambda p: p.day_of_week != "*" and p.day_of_month == "*"),
    ("monthly",      lambda p: p.day_of_month != "*" and p.day_of_week == "*"),
    ("on_weekday",   lambda p: p.day_of_week in ("1-5", "mon-fri")),
    ("on_weekend",   lambda p: p.day_of_week in ("6,0", "0,6", "sat,sun", "sun,sat")),
    ("has_step",     lambda p: any("/" in str(getattr(p, f)) for f in
                                   ("minute", "hour", "day_of_month", "month", "day_of_week"))),
    ("has_range",    lambda p: any("-" in str(getattr(p, f)) for f in
                                   ("minute", "hour", "day_of_month", "month", "day_of_week"))),
    ("yearly",       lambda p: p.month != "*" and p.day_of_month != "*" and p.day_of_week == "*"),
]


def tag(expression: str, parse_result: ParseResult | None = None) -> TagResult:
    """Return a TagResult with all matching tags for *expression*."""
    from crontab_lint.parser import parse

    if parse_result is None:
        parse_result = parse(expression)

    if not parse_result.valid:
        return TagResult(expression=expression, tags=[], valid=False)

    matched: List[str] = []
    for name, predicate in _KNOWN_TAGS:
        try:
            if predicate(parse_result):
                matched.append(name)
        except Exception:
            pass

    return TagResult(expression=expression, tags=matched, valid=True)
