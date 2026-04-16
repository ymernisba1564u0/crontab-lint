"""lint command – validate one or more cron expressions."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from crontab_lint.reporter import build_report
from crontab_lint.formatter import format_text, format_json
from crontab_lint.validator import validate_many


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("lint", help="Validate cron expression(s)")
    p.add_argument("expressions", nargs="+", metavar="EXPR",
                   help="Cron expression(s) to validate")
    p.add_argument("--timezone", "-tz", default="UTC",
                   help="Timezone for next-occurrence preview (default: UTC)")
    p.add_argument("--count", "-n", type=int, default=5,
                   help="Number of upcoming occurrences to show (default: 5)")
    p.add_argument("--format", "-f", choices=["text", "json"], default="text",
                   dest="output_format")
    p.set_defaults(func=handle)


def handle(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    results = validate_many(args.expressions)
    reports = [
        build_report(expr, args.timezone, args.count)
        for expr in args.expressions
    ]

    if args.output_format == "json":
        payload = [json.loads(format_json(r)) for r in reports]
        out.write(json.dumps(payload, indent=2))
        out.write("\n")
    else:
        for report in reports:
            out.write(format_text(report))
            out.write("\n")

    all_valid = all(r.errors == [] for r in reports)
    return 0 if all_valid else 1
