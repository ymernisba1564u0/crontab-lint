"""Normalize cron expressions to a canonical form."""
from __future__ import annotations

from dataclasses import dataclass

from .parser import ParseResult, parse

_MONTH_NAMES = ["jan","feb","mar","apr","may","jun",
                "jul","aug","sep","oct","nov","dec"]
_DOW_NAMES   = ["sun","mon","tue","wed","thu","fri","sat"]


@dataclass
class NormalizeResult:
    original: str
    normalized: str
    changed: bool
    parse_result: ParseResult | None
    error: str | None


def _normalize_field(raw: str, names: list[str]) -> str:
    """Lower-case alias substitution + trim whitespace."""
    token = raw.strip()
    for i, name in enumerate(names):
        token = token.replace(name, str(i + 1))
        token = token.replace(name.upper(), str(i + 1))
        token = token.replace(name.capitalize(), str(i + 1))
    return token


def normalize(expression: str) -> NormalizeResult:
    """Return a canonical representation of *expression*.

    Aliases (JAN, MON …) are replaced with their numeric equivalents.
    Leading/trailing whitespace and redundant internal spaces are removed.
    """
    pr = parse(expression)
    if not pr.valid:
        return NormalizeResult(
            original=expression,
            normalized=expression,
            changed=False,
            parse_result=pr,
            error=pr.error,
        )

    parts = expression.strip().split()
    minute, hour, dom, month, dow = parts

    month = _normalize_field(month, _MONTH_NAMES)
    dow   = _normalize_field(dow,   _DOW_NAMES)

    normalized = " ".join([minute, hour, dom, month, dow])
    return NormalizeResult(
        original=expression,
        normalized=normalized,
        changed=normalized != expression.strip(),
        parse_result=pr,
        error=None,
    )
