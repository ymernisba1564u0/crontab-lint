"""Cron expression parser and validator."""

import re
from dataclasses import dataclass
from typing import Optional

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronField:
    name: str
    raw: str
    min_val: int
    max_val: int


@dataclass
class ParseResult:
    expression: str
    fields: list[CronField]
    is_valid: bool
    errors: list[str]


def _resolve_aliases(value: str, aliases: dict) -> str:
    for alias, num in aliases.items():
        value = re.sub(rf"\b{alias}\b", str(num), value, flags=re.IGNORECASE)
    return value


def _validate_field(field: CronField) -> list[str]:
    errors = []
    raw = field.raw
    min_v, max_v = field.min_val, field.max_val

    if field.name == "month":
        raw = _resolve_aliases(raw, MONTH_ALIASES)
    elif field.name == "day_of_week":
        raw = _resolve_aliases(raw, DOW_ALIASES)

    parts = raw.split(",")
    for part in parts:
        if part == "*":
            continue
        step_match = re.match(r"^(\*|\d+(?:-\d+)?)/(\d+)$", part)
        if step_match:
            step = int(step_match.group(2))
            if step == 0:
                errors.append(f"[{field.name}] Step value cannot be zero in '{part}'")
            continue
        range_match = re.match(r"^(\d+)-(\d+)$", part)
        if range_match:
            lo, hi = int(range_match.group(1)), int(range_match.group(2))
            if lo > hi:
                errors.append(f"[{field.name}] Invalid range '{part}': start > end")
            elif lo < min_v or hi > max_v:
                errors.append(f"[{field.name}] Range '{part}' out of bounds ({min_v}-{max_v})")
            continue
        if re.match(r"^\d+$", part):
            val = int(part)
            if val < min_v or val > max_v:
                errors.append(f"[{field.name}] Value {val} out of bounds ({min_v}-{max_v})")
            continue
        errors.append(f"[{field.name}] Invalid token '{part}'")
    return errors


def parse(expression: str) -> ParseResult:
    parts = expression.strip().split()
    errors = []

    if len(parts) != 5:
        return ParseResult(
            expression=expression,
            fields=[],
            is_valid=False,
            errors=[f"Expected 5 fields, got {len(parts)}"],
        )

    fields = [
        CronField(name=FIELD_NAMES[i], raw=parts[i],
                  min_val=FIELD_RANGES[FIELD_NAMES[i]][0],
                  max_val=FIELD_RANGES[FIELD_NAMES[i]][1])
        for i in range(5)
    ]

    for field in fields:
        errors.extend(_validate_field(field))

    return ParseResult(
        expression=expression,
        fields=fields,
        is_valid=len(errors) == 0,
        errors=errors,
    )
