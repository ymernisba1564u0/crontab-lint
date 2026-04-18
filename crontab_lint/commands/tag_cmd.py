"""CLI command: tag — categorize a cron expression by schedule pattern."""
from __future__ import annotations
import argparse
import json
import sys
from crontab_lint.tags import tag


def register(subparsers: argparse._SubParsersAction) -> None:
    p = subparsers.add_parser("tag", help="Categorize a cron expression by schedule pattern")
    p.add_argument("expression", help="Cron expression to tag")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=handle)


def _format_text(result) -> str:
    lines: list[str] = []
    status = "✔" if result.valid else "✘"
    lines.append(f"{status}  {result.expression}")
    if result.valid:
        if result.tags:
            lines.append("Tags: " + ", ".join(result.tags))
        else:
            lines.append("Tags: (none matched)")
    else:
        lines.append("Invalid expression — cannot tag.")
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    result = tag(args.expression)

    if args.format == "json":
        print(json.dumps({
            "expression": result.expression,
            "valid": result.valid,
            "tags": result.tags,
        }))
    else:
        print(_format_text(result))

    return 0 if result.valid else 1
