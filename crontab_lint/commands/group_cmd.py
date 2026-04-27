"""CLI command: group cron expressions from a file by a chosen field or tag."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from crontab_lint.grouper import group


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser(
        "group",
        help="Group cron expressions by field or tag.",
    )
    p.add_argument("file", help="File containing one cron expression per line.")
    p.add_argument(
        "--by",
        dest="group_by",
        default="tag",
        choices=["tag", "minute", "hour", "dom", "month", "dow"],
        help="Field or characteristic to group by (default: tag).",
    )
    p.add_argument(
        "--format",
        dest="fmt",
        default="text",
        choices=["text", "json"],
        help="Output format (default: text).",
    )
    p.set_defaults(func=handle)


def _read_file(path: str) -> list[str]:
    return [
        line.strip()
        for line in Path(path).read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]


def _format_text(result) -> str:
    lines = [f"Grouped {result.total} expression(s) into {result.group_count} group(s) by '{result.group_by}':\n"]
    for key in sorted(result.groups):
        members = result.groups[key]
        lines.append(f"  [{key}] ({len(members)})")
        for expr in members:
            lines.append(f"    - {expr}")
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    try:
        expressions = _read_file(args.file)
    except FileNotFoundError:
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        return 2

    result = group(expressions, group_by=args.group_by)

    if args.fmt == "json":
        print(json.dumps({
            "group_by": result.group_by,
            "total": result.total,
            "group_count": result.group_count,
            "groups": result.groups,
        }, indent=2))
    else:
        print(_format_text(result))

    return 0
