"""CLI command: heatmap — show frequency distribution for a cron expression."""
from __future__ import annotations

import argparse
import json
import sys
from typing import List

from crontab_lint.heatmap import build_heatmap, format_heatmap_text
from crontab_lint.validator import validate


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "heatmap",
        help="Show hour/weekday/month frequency heatmap for a cron expression",
    )
    p.add_argument("expression", help="Cron expression (quote it)")
    p.add_argument("--timezone", default="UTC", help="Timezone name (default: UTC)")
    p.add_argument("--count", type=int, default=500, help="Occurrences to sample (default: 500)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=handle)


def handle(args: argparse.Namespace) -> int:
    validation = validate(args.expression)
    if not validation.valid:
        msg = "; ".join(validation.errors)
        if args.format == "json":
            print(json.dumps({"valid": False, "errors": validation.errors}))
        else:
            print(f"✗ Invalid expression: {msg}", file=sys.stderr)
        return 1

    try:
        result = build_heatmap(
            args.expression,
            timezone=args.timezone,
            count=args.count,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps({
            "expression": result.expression,
            "timezone": result.timezone,
            "total": result.total,
            "hours": {str(k): v for k, v in sorted(result.hours.items())},
            "weekdays": {str(k): v for k, v in sorted(result.weekdays.items())},
            "months": {str(k): v for k, v in sorted(result.months.items())},
        }))
    else:
        print(format_heatmap_text(result))

    return 0
