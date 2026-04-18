"""CLI command: timeline — show occurrences over a time window."""
from __future__ import annotations
import argparse
import json
import sys
from typing import Any

from crontab_lint.timeline import build_timeline, format_timeline_text


def register(subparsers: Any) -> None:
    p: argparse.ArgumentParser = subparsers.add_parser(
        "timeline", help="Show cron occurrences over a time window"
    )
    p.add_argument("expression", help="Cron expression (5 fields)")
    p.add_argument("--tz", default="UTC", help="Timezone name (default: UTC)")
    p.add_argument("--hours", type=int, default=24, help="Window size in hours (default: 24)")
    p.add_argument("--count", type=int, default=100, help="Max occurrences to fetch (default: 100)")
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.set_defaults(func=handle)


def handle(args: argparse.Namespace) -> int:
    result = build_timeline(
        args.expression,
        timezone=args.tz,
        window_hours=args.hours,
        count=args.count,
    )

    if args.fmt == "json":
        data = {
            "expression": result.expression,
            "timezone": result.timezone,
            "window_hours": result.window_hours,
            "valid": result.valid,
            "error": result.error,
            "occurrences": [dt.isoformat() for dt in result.occurrences],
        }
        print(json.dumps(data, indent=2))
    else:
        print(format_timeline_text(result))

    return 0 if result.valid else 1
