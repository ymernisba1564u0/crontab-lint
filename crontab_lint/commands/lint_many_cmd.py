"""CLI command: lint-many — lint multiple expressions from a file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import List

from crontab_lint.linter import lint_many, summary_counts


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("lint-many", help="Lint expressions from a file")
    p.add_argument("file", help="Path to file with one cron expression per line")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=handle)


def _read_file(path: str) -> List[str]:
    lines = Path(path).read_text().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def _format_text(results, counts) -> str:
    lines = []
    for r in results:
        mark = "\u2713" if r.valid else "\u2717"
        lines.append(f"  {mark}  {r.expression}")
        for e in r.errors:
            lines.append(f"       error: {e}")
        for w in r.warnings:
            lines.append(f"       warning: {w}")
    lines.append("")
    lines.append(
        f"Total: {counts['total']}  Valid: {counts['valid']}  "
        f"Invalid: {counts['invalid']}  With warnings: {counts['with_warnings']}"
    )
    return "\n".join(lines)


def handle(ns: argparse.Namespace) -> int:
    try:
        expressions = _read_file(ns.file)
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
        return 2

    results = lint_many(expressions)
    counts = summary_counts(results)

    if ns.format == "json":
        payload = {
            "summary": counts,
            "results": [
                {"expression": r.expression, "valid": r.valid,
                 "errors": r.errors, "warnings": r.warnings}
                for r in results
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(_format_text(results, counts))

    return 0 if counts["invalid"] == 0 else 1
