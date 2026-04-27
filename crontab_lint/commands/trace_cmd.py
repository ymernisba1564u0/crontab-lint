"""CLI sub-command: trace — show recent past occurrences of a cron expression."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone

from ..tracer import trace


def register(subparsers) -> None:
    parser = subparsers.add_parser(
        "trace",
        help="Show the N most-recent past occurrences of a cron expression.",
    )
    parser.add_argument("expression", help="Cron expression (quoted).")
    parser.add_argument(
        "--timezone", "-z", default="UTC", metavar="TZ",
        help="IANA timezone name (default: UTC).",
    )
    parser.add_argument(
        "--count", "-n", type=int, default=5, metavar="N",
        help="Number of past occurrences to return (default: 5, max: 100).",
    )
    parser.add_argument(
        "--before", metavar="ISO8601",
        help="Upper-bound datetime in ISO-8601 format (default: now).",
    )
    parser.add_argument(
        "--format", "-f", choices=["text", "json"], default="text",
        dest="output_format",
    )
    parser.set_defaults(func=handle)


def _parse_before(value: str) -> datetime:
    """Parse an ISO-8601 string into a UTC-aware datetime."""
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _format_text(result) -> str:
    lines = []
    if not result.valid:
        lines.append(f"\u2718 Invalid expression: {result.expression}")
        for err in result.errors:
            lines.append(f"  - {err}")
        return "\n".join(lines)

    lines.append(f"\u2714 {result.expression}  [tz: {result.timezone}]")
    lines.append(f"Last {len(result.occurrences)} occurrence(s):")
    for occ in result.occurrences:
        lines.append(f"  {occ.isoformat(timespec='seconds')}")
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    before = None
    if getattr(args, "before", None):
        try:
            before = _parse_before(args.before)
        except ValueError as exc:
            print(f"Error parsing --before: {exc}", file=sys.stderr)
            return 2

    result = trace(
        args.expression,
        tz_name=args.timezone,
        count=args.count,
        before=before,
    )

    if args.output_format == "json":
        payload = {
            "expression": result.expression,
            "timezone": result.timezone,
            "valid": result.valid,
            "errors": result.errors,
            "occurrences": [
                occ.isoformat(timespec="seconds") for occ in result.occurrences
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(_format_text(result))

    return 0 if result.valid else 1
