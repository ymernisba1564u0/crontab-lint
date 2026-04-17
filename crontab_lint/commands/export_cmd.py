"""CLI command: export cron expressions to JSON or CSV."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from crontab_lint.exporter import export_json, export_csv


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("export", help="Export cron expressions to JSON or CSV")
    p.add_argument("file", help="File containing cron expressions (one per line)")
    p.add_argument("--format", choices=["json", "csv"], default="json", dest="fmt")
    p.add_argument("--timezone", default="UTC")
    p.add_argument("--count", type=int, default=1, help="Next occurrences to include")
    p.add_argument("--output", default=None, help="Output file (default: stdout)")
    p.set_defaults(func=handle)


def _read_file(path: str) -> list[str]:
    lines = Path(path).read_text().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.startswith("#")]


def handle(args: argparse.Namespace) -> int:
    try:
        expressions = _read_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 1

    if args.fmt == "json":
        output = export_json(expressions, timezone=args.timezone, count=args.count)
    else:
        output = export_csv(expressions, timezone=args.timezone, count=args.count)

    if args.output:
        Path(args.output).write_text(output)
    else:
        print(output)

    return 0
