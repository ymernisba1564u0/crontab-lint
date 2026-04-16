"""CLI sub-command: normalize a cron expression."""
from __future__ import annotations

import argparse
import json
import sys

from ..normalizer import normalize


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("normalize", help="Normalize a cron expression")
    p.add_argument("expression", help="Cron expression to normalize")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        dest="fmt",
    )
    p.set_defaults(func=handle)


def _format_text(result) -> str:
    lines = []
    if result.error:
        lines.append(f"\u2718 Invalid expression: {result.error}")
        return "\n".join(lines)
    lines.append(f"Original  : {result.original}")
    lines.append(f"Normalized: {result.normalized}")
    if result.changed:
        lines.append("(expression was changed)")
    else:
        lines.append("(no changes needed)")
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    result = normalize(args.expression)

    if args.fmt == "json":
        payload = {
            "original": result.original,
            "normalized": result.normalized,
            "changed": result.changed,
            "valid": result.error is None,
            "error": result.error,
        }
        print(json.dumps(payload))
        return 0 if result.error is None else 1

    print(_format_text(result))
    return 0 if result.error is None else 1
