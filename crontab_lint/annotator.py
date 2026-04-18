"""Annotate a cron expression with inline field labels and descriptions."""
from dataclasses import dataclass
from typing import Optional
from crontab_lint.parser import parse, ParseResult

_FIELD_NAMES = ["minute", "hour", "day-of-month", "month", "day-of-week"]

_FIELD_SHORT = ["min", "hr", "dom", "mon", "dow"]


@dataclass
class AnnotationField:
    name: str
    short: str
    raw: str
    description: str


@dataclass
class AnnotateResult:
    expression: str
    valid: bool
    error: Optional[str]
    fields: list  # list[AnnotationField]

    def annotated_line(self) -> str:
        """Return a single line with each token labelled."""
        if not self.valid:
            return self.expression
        parts = [f"{f.short}={f.raw}" for f in self.fields]
        return "  ".join(parts)


def _describe(name: str, raw: str) -> str:
    if raw == "*":
        return f"every {name}"
    if "/" in raw:
        base, step = raw.split("/", 1)
        base_str = "any" if base == "*" else base
        return f"every {step} {name}(s) starting at {base_str}"
    if "-" in raw:
        lo, hi = raw.split("-", 1)
        return f"{name} {lo} through {hi}"
    if "," in raw:
        return f"{name} in ({raw})"
    return f"{name} = {raw}"


def annotate(expression: str) -> AnnotateResult:
    result = parse(expression)
    if not result.valid:
        return AnnotateResult(
            expression=expression,
            valid=False,
            error=result.error,
            fields=[],
        )
    tokens = expression.split()
    fields = [
        AnnotationField(
            name=_FIELD_NAMES[i],
            short=_FIELD_SHORT[i],
            raw=tokens[i],
            description=_describe(_FIELD_NAMES[i], tokens[i]),
        )
        for i in range(5)
    ]
    return AnnotateResult(expression=expression, valid=True, error=None, fields=fields)
