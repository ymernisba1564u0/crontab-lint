# crontab-lint

> A CLI tool that validates and explains cron expressions with timezone-aware scheduling previews.

---

## Installation

```bash
pip install crontab-lint
```

Or with [pipx](https://pypa.github.io/pipx/) for isolated installs:

```bash
pipx install crontab-lint
```

---

## Usage

Validate a cron expression and preview the next scheduled runs:

```bash
crontab-lint "*/15 9-17 * * 1-5" --timezone America/New_York --preview 5
```

**Output:**
```
✔ Valid cron expression
  Description: Every 15 minutes, between 09:00 and 17:59, Monday through Friday

  Next 5 occurrences (America/New_York):
    1. 2024-03-11 09:00:00 EST
    2. 2024-03-11 09:15:00 EST
    3. 2024-03-11 09:30:00 EST
    4. 2024-03-11 09:45:00 EST
    5. 2024-03-11 10:00:00 EST
```

Validate without a preview:

```bash
crontab-lint "0 25 * * *"
```

```
✘ Invalid cron expression
  Error: Hour field value '25' out of range (0-23)
```

---

## Options

| Flag | Description | Default |
|------|-------------|---------|
| `--timezone`, `-tz` | IANA timezone for scheduling preview | `UTC` |
| `--preview`, `-n` | Number of upcoming runs to display | `3` |
| `--quiet`, `-q` | Exit with code only, no output | `False` |

---

## License

MIT © 2024 [crontab-lint contributors](https://github.com/your-org/crontab-lint)