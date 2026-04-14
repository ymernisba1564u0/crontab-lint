"""Command-line interface for crontab-lint."""

import argparse
import sys
from datetime import datetime, timezone

from crontab_lint.explainer import explain
from crontab_lint.parser import parse
from crontab_lint.scheduler import SchedulerError, next_occurrences


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Validate and explain cron expressions with scheduling previews.",
    )
    p.add_argument("expression", help="Cron expression in quotes, e.g. '*/5 * * * *'")
    p.add_argument(
        "--timezone",
        "-tz",
        default="UTC",
        metavar="TZ",
        help="IANA timezone for the schedule preview (default: UTC).",
    )
    p.add_argument(
        "--next",
        "-n",
        type=int,
        default=5,
        metavar="N",
        dest="count",
        help="Number of upcoming occurrences to display (default: 5).",
    )
    return p


def main(argv=None) -> int:  # noqa: D401
    """Entry point; returns an exit code."""
    args = _build_parser().parse_args(argv)
    expression: str = args.expression

    result = parse(expression)

    if not result.valid:
        print(f"[ERROR] Invalid expression: {result.error}", file=sys.stderr)
        return 1

    print(f"Expression : {expression}")
    print(f"Explanation: {explain(result)}")
    print()

    try:
        occurrences = next_occurrences(
            expression,
            count=args.count,
            tz_name=args.timezone,
        )
    except SchedulerError as exc:
        print(f"[ERROR] {exc}", file=sys.stderr)
        return 1

    tz_label = args.timezone
    print(f"Next {args.count} occurrences ({tz_label}):")
    for dt in occurrences:
        print(f"  {dt.strftime('%Y-%m-%d %H:%M %Z')}")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
