"""CLI command: annotate — show inline field labels for a cron expression."""
import argparse
import json
from crontab_lint.annotator import annotate


def register(subparsers) -> None:
    p = subparsers.add_parser("annotate", help="Annotate each field of a cron expression")
    p.add_argument("expression", help="Cron expression to annotate")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.set_defaults(func=handle)


def _format_text(result) -> str:
    lines = []
    if not result.valid:
        lines.append(f"✗ Invalid: {result.error}")
        return "\n".join(lines)
    lines.append(f"✓ {result.expression}")
    lines.append("")
    lines.append(result.annotated_line())
    lines.append("")
    for f in result.fields:
        lines.append(f"  {f.name:<14} {f.raw:<12} {f.description}")
    return "\n".join(lines)


def handle(args: argparse.Namespace) -> int:
    result = annotate(args.expression)
    if args.format == "json":
        data = {
            "expression": result.expression,
            "valid": result.valid,
            "error": result.error,
            "fields": [
                {"name": f.name, "short": f.short, "raw": f.raw, "description": f.description}
                for f in result.fields
            ],
        }
        print(json.dumps(data, indent=2))
    else:
        print(_format_text(result))
    return 0 if result.valid else 1
