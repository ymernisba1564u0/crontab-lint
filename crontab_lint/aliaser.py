"""Resolve and list all supported cron field aliases."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

MONTH_ALIASES: Dict[str, int] = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DOW_ALIASES: Dict[str, int] = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}

SPECIAL_ALIASES: Dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


@dataclass
class AliasInfo:
    alias: str
    value: int | str
    field: str
    description: str


@dataclass
class AliasReport:
    month_aliases: List[AliasInfo] = field(default_factory=list)
    dow_aliases: List[AliasInfo] = field(default_factory=list)
    special_aliases: List[AliasInfo] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.month_aliases) + len(self.dow_aliases) + len(self.special_aliases)


def resolve_special(expression: str) -> str | None:
    """Return the expanded form of a special alias, or None if not recognised."""
    return SPECIAL_ALIASES.get(expression.lower())


def list_aliases() -> AliasReport:
    """Return an AliasReport enumerating every supported alias."""
    month = [
        AliasInfo(alias=k, value=v, field="month",
                  description=f"Month {v} ({k.capitalize()})")
        for k, v in MONTH_ALIASES.items()
    ]
    dow = [
        AliasInfo(alias=k, value=v, field="dow",
                  description=f"Day-of-week {v} ({k.capitalize()})")
        for k, v in DOW_ALIASES.items()
    ]
    special = [
        AliasInfo(alias=k, value=v, field="special",
                  description=f"Expands to '{v}'")
        for k, v in SPECIAL_ALIASES.items()
    ]
    return AliasReport(month_aliases=month, dow_aliases=dow, special_aliases=special)
