"""CLI command: compare similarity of two cron expressions."""
from __future__ import annotations
import argparse
import json
import sys
from crontab_lint.similarity import similarity


def register(subparsers) -> None:
    p = subparsers.add_parser(
        "similarity",
        help="Score the similarity between two cron expressions (0.0–1.0)",
    )
    p.add_argument("expression_a", help="First cron expression")
    p.add_argument("expression_b", help="Second cron expression")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=handle)


def _format_text(result) -> str:
    lines = [
        f"Expression A : {result.expression_a}",
        f"Expression B : {result.expression_b}",
    ]
    if not result.both_valid:
        lines.append(f"✗ Cannot compare — {result.error}")
        return "\n".join(lines)
    bar_len = int(result.score * 20)
    bar = "█" * bar_len + "░" * (20 - bar_len)
    lines += [
        f"Score        : {result.score:.2f}  [{bar}]",
        f"Matching     : {result.matching_fields}/{result.total_fields} fields",
    ]
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    result = similarity(args.expression_a, args.expression_b)

    if args.format == "json":
        print(
            json.dumps(
                {
                    "expression_a": result.expression_a,
                    "expression_b": result.expression_b,
                    "score": result.score,
                    "matching_fields": result.matching_fields,
                    "total_fields": result.total_fields,
                    "both_valid": result.both_valid,
                    "error": result.error,
                },
                indent=2,
            )
        )
    else:
        print(_format_text(result))

    return 0 if result.both_valid else 1
