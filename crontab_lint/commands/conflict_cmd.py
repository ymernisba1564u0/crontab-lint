"""CLI command: detect scheduling conflicts across multiple cron expressions."""
from __future__ import annotations
import argparse
import json
import sys
from ..conflict import find_conflicts


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = subparsers.add_parser("conflict", help="Detect scheduling conflicts between cron expressions")
    p.add_argument("expressions", nargs="+", help="Two or more cron expressions")
    p.add_argument("--timezone", default="UTC", help="Timezone for scheduling (default: UTC)")
    p.add_argument("--count", type=int, default=50, help="Occurrences to check per expression")
    p.add_argument("--format", choices=["text", "json"], default="text", dest="fmt")
    p.set_defaults(func=handle)


def _format_text(result) -> str:
    lines = [f"Checked {result.checked_occurrences} occurrences per expression."]
    if not result.conflicts:
        lines.append("✔ No conflicts detected.")
    else:
        lines.append(f"✖ {result.total_conflicts} conflict(s) detected:")
        for a, b, ts in result.conflicts:
            lines.append(f"  [{ts}]  '{a}'  ↔  '{b}'")
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    if len(args.expressions) < 2:
        print("Error: provide at least two expressions.", file=sys.stderr)
        return 2

    result = find_conflicts(args.expressions, timezone=args.timezone, count=args.count)

    if args.fmt == "json":
        print(json.dumps({
            "expressions": result.expressions,
            "total_conflicts": result.total_conflicts,
            "checked_occurrences": result.checked_occurrences,
            "conflicts": [{"expr_a": a, "expr_b": b, "time": ts} for a, b, ts in result.conflicts],
        }, indent=2))
    else:
        print(_format_text(result))

    return 1 if result.total_conflicts > 0 else 0
