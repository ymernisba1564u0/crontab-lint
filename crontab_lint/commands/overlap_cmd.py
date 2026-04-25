"""CLI command: detect overlapping cron expressions from a file."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ..overlapper import find_overlaps


def register(sub: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
    p = sub.add_parser("overlap", help="Detect overlapping cron expressions")
    p.add_argument("file", help="File with one cron expression per line")
    p.add_argument("--timezone", "-z", default="UTC", help="Timezone (default: UTC)")
    p.add_argument(
        "--threshold",
        "-t",
        type=int,
        default=1,
        help="Minimum shared occurrences to count as overlap (default: 1)",
    )
    p.add_argument(
        "--format", "-f", choices=["text", "json"], default="text"
    )
    p.set_defaults(func=handle)


def _read_file(path: str) -> list[str]:
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [ln.strip() for ln in lines if ln.strip() and not ln.startswith("#")]


def _format_text(result) -> str:
    lines: list[str] = []
    lines.append(f"Expressions checked : {len(result.expressions)}")
    lines.append(f"Pairs checked       : {result.total_pairs_checked}")
    lines.append(f"Overlapping pairs   : {len(result.overlaps)}")
    if result.overlaps:
        lines.append("")
        lines.append("Overlaps:")
        for a, b, count in result.overlaps:
            lines.append(f"  [{count:>3} shared]  {a!r}  <->  {b!r}")
    else:
        lines.append("✔ No overlapping expressions found.")
    return "\n".join(lines)


def handle(ns: argparse.Namespace) -> int:
    expressions = _read_file(ns.file)
    if not expressions:
        print("No expressions found in file.", file=sys.stderr)
        return 1

    result = find_overlaps(expressions, timezone=ns.timezone, threshold=ns.threshold)

    if getattr(ns, "format", "text") == "json":
        payload = {
            "timezone": result.timezone,
            "expressions": result.expressions,
            "total_pairs_checked": result.total_pairs_checked,
            "overlapping_pairs": [
                {"a": a, "b": b, "shared_occurrences": c}
                for a, b, c in result.overlaps
            ],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(_format_text(result))

    return 1 if result.overlaps else 0
