"""Output formatters for cron lint results."""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from crontab_lint.parser import ParseResult


@dataclass
class LintReport:
    expression: str
    timezone: str
    is_valid: bool
    explanation: Optional[str]
    errors: List[str]
    next_occurrences: List[datetime]


def format_text(report: LintReport) -> str:
    """Format a LintReport as human-readable text."""
    lines = []
    lines.append(f"Expression : {report.expression}")
    lines.append(f"Timezone   : {report.timezone}")

    if report.is_valid:
        lines.append("Status     : \u2713 Valid")
        lines.append(f"Meaning    : {report.explanation}")
        if report.next_occurrences:
            lines.append("Next runs  :")
            for dt in report.next_occurrences:
                lines.append(f"  - {dt.strftime('%Y-%m-%d %H:%M:%S %Z')}")
    else:
        lines.append("Status     : \u2717 Invalid")
        for err in report.errors:
            lines.append(f"  Error: {err}")

    return "\n".join(lines)


def format_json(report: LintReport) -> str:
    """Format a LintReport as a JSON string."""
    import json

    data = {
        "expression": report.expression,
        "timezone": report.timezone,
        "valid": report.is_valid,
        "explanation": report.explanation,
        "errors": report.errors,
        "next_occurrences": [
            dt.strftime("%Y-%m-%dT%H:%M:%S%z") for dt in report.next_occurrences
        ],
    }
    return json.dumps(data, indent=2)
