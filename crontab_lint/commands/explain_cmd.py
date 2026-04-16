"""CLI command: explain a cron expression in plain English."""
from __future__ import annotations

import argparse
import json

from crontab_lint.validator import validate
from crontab_lint.explainer import explain


def register(subparsers: argparse._SubParsersAction) -> None:  # noqa: SLF001
    p = subparsers.add_parser("explain", help="Explain a cron expression in plain English")
    p.add_argument("expression", help="Cron expression (quote it: '* * * * *')")
    p.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )
    p.set_defaults(func=handle)


def handle(args: argparse.Namespace) -> int:
    result = validate(args.expression)

    if not result.is_valid:
        if args.format == "json":
            print(json.dumps({"valid": False, "errors": result.errors}))
        else:
            print(f"\u2718 Invalid expression: {args.expression}")
            for err in result.errors:
                print(f"  - {err}")
        return 1

    explanation = explain(result.parse_result)  # type: ignore[arg-type]

    if args.format == "json":
        print(
            json.dumps(
                {
                    "valid": True,
                    "expression": args.expression,
                    "explanation": explanation,
                    "warnings": result.warnings,
                }
            )
        )
    else:
        _format_text(args.expression, explanation, result.warnings)

    return 0


def _format_text(expression: str, explanation: str, warnings: list[str]) -> None:
    print(f"\u2714 {expression}")
    print(f"  {explanation}")
    if warnings:
        print("  Warnings:")
        for w in warnings:
            print(f"    \u26a0 {w}")
