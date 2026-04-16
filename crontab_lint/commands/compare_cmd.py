"""CLI command: compare two cron expressions for semantic equivalence."""
import argparse
import json
import sys
from ..comparator import compare


def register(subparsers) -> None:
    p = subparsers.add_parser("compare", help="Compare two cron expressions semantically")
    p.add_argument("expression_a", help="First cron expression")
    p.add_argument("expression_b", help="Second cron expression")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=handle)


def _format_text(result) -> str:
    lines = []
    if not result.both_valid:
        lines.append("✗ One or both expressions are invalid.")
        if result.errors_a:
            lines.append(f"  Expression A errors: {', '.join(result.errors_a)}")
        if result.errors_b:
            lines.append(f"  Expression B errors: {', '.join(result.errors_b)}")
        return "\n".join(lines)

    symbol = "✔" if result.are_equivalent else "✗"
    status = "equivalent" if result.are_equivalent else "not equivalent"
    lines.append(f"{symbol} Expressions are {status}.")
    lines.append(f"  A normalized: {result.normalized_a}")
    lines.append(f"  B normalized: {result.normalized_b}")
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    result = compare(args.expression_a, args.expression_b)

    if args.format == "json":
        print(json.dumps({
            "expression_a": result.expression_a,
            "expression_b": result.expression_b,
            "normalized_a": result.normalized_a,
            "normalized_b": result.normalized_b,
            "are_equivalent": result.are_equivalent,
            "both_valid": result.both_valid,
            "errors_a": result.errors_a,
            "errors_b": result.errors_b,
        }))
    else:
        print(_format_text(result))

    return 0 if (result.both_valid and result.are_equivalent) else 1
