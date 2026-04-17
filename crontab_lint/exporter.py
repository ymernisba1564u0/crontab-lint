"""Export cron expressions and their metadata to various formats."""
from __future__ import annotations

import csv
import io
import json
from dataclasses import dataclass, field
from typing import List

from crontab_lint.validator import validate
from crontab_lint.explainer import explain
from crontab_lint.scheduler import next_occurrences


@dataclass
class ExportRow:
    expression: str
    valid: bool
    explanation: str
    errors: List[str] = field(default_factory=list)
    next_run: str = ""


def _build_rows(expressions: List[str], timezone: str = "UTC", count: int = 1) -> List[ExportRow]:
    rows: List[ExportRow] = []
    for expr in expressions:
        result = validate(expr)
        explanation = ""
        next_run = ""
        if result.valid and result.parse_result:
            explanation = explain(result.parse_result)
            try:
                occ = next_occurrences(expr, timezone=timezone, count=count)
                next_run = occ[0].isoformat() if occ else ""
            except Exception:
                next_run = ""
        rows.append(ExportRow(
            expression=expr,
            valid=result.valid,
            explanation=explanation,
            errors=result.errors,
            next_run=next_run,
        ))
    return rows


def export_json(expressions: List[str], timezone: str = "UTC", count: int = 1) -> str:
    rows = _build_rows(expressions, timezone=timezone, count=count)
    data = [
        {
            "expression": r.expression,
            "valid": r.valid,
            "explanation": r.explanation,
            "errors": r.errors,
            "next_run": r.next_run,
        }
        for r in rows
    ]
    return json.dumps(data, indent=2)


def export_csv(expressions: List[str], timezone: str = "UTC", count: int = 1) -> str:
    rows = _build_rows(expressions, timezone=timezone, count=count)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["expression", "valid", "explanation", "errors", "next_run"])
    for r in rows:
        writer.writerow([
            r.expression,
            r.valid,
            r.explanation,
            ";".join(r.errors),
            r.next_run,
        ])
    return buf.getvalue()
