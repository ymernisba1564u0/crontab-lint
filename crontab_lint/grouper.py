"""Group cron expressions by a shared characteristic (field pattern or tag)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from crontab_lint.validator import validate
from crontab_lint.tags import tag


@dataclass
class GroupResult:
    expressions: List[str]
    groups: Dict[str, List[str]]
    group_by: str
    total: int
    group_count: int


def _group_key_field(expression: str, field_index: int) -> str:
    """Return the raw value of a single cron field as the group key."""
    parts = expression.strip().split()
    if len(parts) != 5:
        return "__invalid__"
    return parts[field_index]


def _group_key_tag(expression: str) -> str:
    """Return the primary tag label as the group key."""
    result = tag(expression)
    if not result.valid:
        return "__invalid__"
    return result.label if result.label else "__untagged__"


_FIELD_NAMES = {"minute": 0, "hour": 1, "dom": 2, "month": 3, "dow": 4}


def group(expressions: List[str], group_by: str = "tag") -> GroupResult:
    """Group *expressions* by *group_by*.

    Parameters
    ----------
    expressions:
        List of raw cron expression strings.
    group_by:
        One of ``"tag"``, ``"minute"``, ``"hour"``, ``"dom"``,
        ``"month"``, or ``"dow"``.
    """
    groups: Dict[str, List[str]] = {}

    for expr in expressions:
        vr = validate(expr)
        if not vr.valid:
            key = "__invalid__"
        elif group_by == "tag":
            key = _group_key_tag(expr)
        elif group_by in _FIELD_NAMES:
            key = _group_key_field(expr, _FIELD_NAMES[group_by])
        else:
            raise ValueError(
                f"Unknown group_by value {group_by!r}. "
                f"Choose from: tag, minute, hour, dom, month, dow."
            )
        groups.setdefault(key, []).append(expr)

    return GroupResult(
        expressions=list(expressions),
        groups=groups,
        group_by=group_by,
        total=len(expressions),
        group_count=len(groups),
    )
