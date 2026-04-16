"""CLI sub-command: summarize a batch of cron expressions."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from ..summarizer import summarize


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("summary", help="Print statistics for a list of cron expressions")
    p.add_argument("file", help="File with one cron expression per line")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=handle)


def _read_file(path: str) -> List[str]:
    with open(path) as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]


def _format_text(report) -> str:
    lines = [
        f"Total      : {report.total}",
        f"Valid      : {report.valid} ({report.valid_pct}%)",
        f"Invalid    : {report.invalid}",
        f"Warnings   : {report.warning_count}",
    ]
    if report.invalid_expressions:
        lines.append("\nInvalid expressions:")
        for expr in report.invalid_expressions:
            lines.append(f"  ✗ {expr}")
    if report.warning_expressions:
        lines.append("\nExpressions with warnings:")
        for expr in report.warning_expressions:
            lines.append(f"  ⚠ {expr}")
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    try:
        expressions = _read_file(args.file)
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    report = summarize(expressions)

    if args.format == "json":
        print(json.dumps({
            "total": report.total,
            "valid": report.valid,
            "invalid": report.invalid,
            "valid_pct": report.valid_pct,
            "warning_count": report.warning_count,
            "invalid_expressions": report.invalid_expressions,
            "warning_expressions": report.warning_expressions,
        }, indent=2))
    else:
        print(_format_text(report))

    return 0 if report.invalid == 0 else 1
