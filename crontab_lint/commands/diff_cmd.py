"""CLI sub-command handler for 'diff' — compare two cron expressions."""

from __future__ import annotations

import argparse
import json
from typing import List

from ..differ import diff, DiffResult


def register(subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    """Register the 'diff' subcommand."""
    parser = subparsers.add_parser(
        "diff",
        help="Compare two cron expressions and highlight differences.",
    )
    parser.add_argument("expression_a", help="First cron expression")
    parser.add_argument("expression_b", help="Second cron expression")
    parser.add_argument(
        "--json", dest="as_json", action="store_true",
        help="Output result as JSON",
    )
    parser.set_defaults(func=handle)


def _format_text(result: DiffResult) -> str:
    lines: List[str] = [
        f"A: {result.expression_a}",
        f"   {result.explanation_a}",
        f"B: {result.expression_b}",
        f"   {result.explanation_b}",
        "",
        f"Summary: {result.summary}",
    ]
    if result.field_diffs:
        lines.append("Changes:")
        for d in result.field_diffs:
            lines.append(f"  • {d}")
    return "\n".join(lines)


def _format_json(result: DiffResult) -> str:
    return json.dumps(
        {
            "expression_a": result.expression_a,
            "expression_b": result.expression_b,
            "valid_a": result.valid_a,
            "valid_b": result.valid_b,
            "explanation_a": result.explanation_a,
            "explanation_b": result.explanation_b,
            "field_diffs": result.field_diffs,
            "summary": result.summary,
        },
        indent=2,
    )


def handle(args: argparse.Namespace) -> None:
    result = diff(args.expression_a, args.expression_b)
    if args.as_json:
        print(_format_json(result))
    else:
        print(_format_text(result))
