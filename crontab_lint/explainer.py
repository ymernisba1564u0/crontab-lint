"""Human-readable explanations for parsed cron fields."""

from crontab_lint.parser import CronField, ParseResult

MONTH_NAMES = [
    "", "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

DOW_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday", "Sunday",  # 7 = Sunday alias
]


def _explain_field(field: CronField) -> str:
    raw = field.raw
    name = field.name.replace("_", " ")

    if raw == "*":
        return f"every {name}"

    if "/" in raw:
        base, step = raw.split("/", 1)
        base_desc = "every" if base == "*" else f"starting at {base}"
        return f"every {step} {name}(s) ({base_desc})"

    if "-" in raw and "," not in raw:
        lo, hi = raw.split("-", 1)
        if field.name == "month":
            lo_name = MONTH_NAMES[int(lo)] if lo.isdigit() else lo
            hi_name = MONTH_NAMES[int(hi)] if hi.isdigit() else hi
            return f"{name} from {lo_name} to {hi_name}"
        if field.name == "day_of_week":
            lo_name = DOW_NAMES[int(lo)] if lo.isdigit() else lo
            hi_name = DOW_NAMES[int(hi)] if hi.isdigit() else hi
            return f"{name} from {lo_name} to {hi_name}"
        return f"{name} from {lo} to {hi}"

    if "," in raw:
        parts = raw.split(",")
        if field.name == "month":
            parts = [MONTH_NAMES[int(p)] if p.isdigit() else p for p in parts]
        elif field.name == "day_of_week":
            parts = [DOW_NAMES[int(p)] if p.isdigit() else p for p in parts]
        return f"{name} on {', '.join(parts)}"

    if raw.isdigit():
        val = int(raw)
        if field.name == "month":
            return f"{name} of {MONTH_NAMES[val]}"
        if field.name == "day_of_week":
            return f"on {DOW_NAMES[val]}"
        return f"at {name} {raw}"

    return f"{name} matching '{raw}'"


def explain(result: ParseResult) -> str:
    if not result.is_valid:
        lines = ["Invalid cron expression:"] + [f"  - {e}" for e in result.errors]
        return "\n".join(lines)

    parts = [_explain_field(f) for f in result.fields]
    minute, hour, dom, month, dow = parts

    summary = f"Runs {minute}, {hour}, {dom}, {month}, {dow}."
    return summary
