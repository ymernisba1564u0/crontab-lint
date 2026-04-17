"""stats command — show aggregate statistics for a file of cron expressions."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from crontab_lint.statistics import compute


def register(subparsers) -> None:
    p = subparsers.add_parser("stats", help="Aggregate statistics for cron expressions")
    p.add_argument("file", help="File with one cron expression per line")
    p.add_argument("--top", type=int, default=3, help="Top N entries to show (default: 3)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=handle)


def _read_file(path: str) -> list[str]:
    lines = Path(path).read_text().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def _format_text(report) -> str:
    lines = [
        f"Total       : {report.total}",
        f"Valid       : {report.valid_count}",
        f"Invalid     : {report.invalid_count}",
        f"Warnings    : {report.warning_count}",
        "",
        "Top minutes : " + ", ".join(f"{v}({c})" for v, c in report.most_common_minutes),
        "Top hours   : " + ", ".join(f"{v}({c})" for v, c in report.most_common_hours),
        "Top DOW     : " + ", ".join(f"{v}({c})" for v, c in report.most_common_dow),
    ]
    if report.error_messages:
        lines += ["", "Errors:"] + [f"  - {e}" for e in report.error_messages[:10]]
    return "\n".join(lines)


def handle(ns: argparse.Namespace) -> int:
    try:
        expressions = _read_file(ns.file)
    except FileNotFoundError:
        print(f"File not found: {ns.file}", file=sys.stderr)
        return 2

    report = compute(expressions, top_n=ns.top)

    if ns.format == "json":
        print(json.dumps({
            "total": report.total,
            "valid": report.valid_count,
            "invalid": report.invalid_count,
            "warnings": report.warning_count,
            "most_common_minutes": report.most_common_minutes,
            "most_common_hours": report.most_common_hours,
            "most_common_dow": report.most_common_dow,
            "error_messages": report.error_messages,
        }))
    else:
        print(_format_text(report))

    return 0 if report.invalid_count == 0 else 1
