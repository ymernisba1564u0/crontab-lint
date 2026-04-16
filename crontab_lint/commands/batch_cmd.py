"""batch command – lint expressions read from a file (one per line)."""
from __future__ import annotations

import argparse
import json
import sys

from crontab_lint.reporter import build_report
from crontab_lint.formatter import format_text, format_json


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser(
        "batch",
        help="Lint cron expressions from a file (one per line)",
    )
    p.add_argument("file", metavar="FILE",
                   help="Path to file containing cron expressions")
    p.add_argument("--timezone", "-tz", default="UTC")
    p.add_argument("--count", "-n", type=int, default=5)
    p.add_argument("--format", "-f", choices=["text", "json"], default="text",
                   dest="output_format")
    p.add_argument("--ignore-comments", action="store_true",
                   help="Skip lines starting with #")
    p.set_defaults(func=handle)


def _read_expressions(path: str, ignore_comments: bool) -> list[str]:
    with open(path) as fh:
        lines = [ln.rstrip("\n") for ln in fh]
    exprs = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if ignore_comments and stripped.startswith("#"):
            continue
        exprs.append(stripped)
    return exprs


def handle(args: argparse.Namespace, out=sys.stdout, err=sys.stderr) -> int:
    try:
        expressions = _read_expressions(args.file, args.ignore_comments)
    except OSError as exc:
        err.write(f"error: {exc}\n")
        return 2

    if not expressions:
        err.write("error: no expressions found in file\n")
        return 2

    reports = [build_report(e, args.timezone, args.count) for e in expressions]

    if args.output_format == "json":
        payload = [json.loads(format_json(r)) for r in reports]
        out.write(json.dumps(payload, indent=2))
        out.write("\n")
    else:
        for report in reports:
            out.write(format_text(report))
            out.write("\n")

    return 0 if all(r.errors == [] for r in reports) else 1
