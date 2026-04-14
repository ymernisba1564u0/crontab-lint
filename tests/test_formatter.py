"""Tests for crontab_lint.formatter and crontab_lint.reporter."""

import json
from datetime import datetime, timezone

import pytest

from crontab_lint.formatter import LintReport, format_text, format_json
from crontab_lint.reporter import build_report


# ---------------------------------------------------------------------------
# format_text
# ---------------------------------------------------------------------------

def _valid_report(**kwargs) -> LintReport:
    defaults = dict(
        expression="0 9 * * 1",
        timezone="UTC",
        is_valid=True,
        explanation="At 09:00 on Monday.",
        errors=[],
        next_occurrences=[],
    )
    defaults.update(kwargs)
    return LintReport(**defaults)


def test_format_text_valid_shows_checkmark():
    report = _valid_report()
    output = format_text(report)
    assert "\u2713 Valid" in output
    assert "0 9 * * 1" in output
    assert "At 09:00 on Monday." in output


def test_format_text_invalid_shows_cross():
    report = _valid_report(
        is_valid=False,
        explanation=None,
        errors=["minute value 99 out of range"],
    )
    output = format_text(report)
    assert "\u2717 Invalid" in output
    assert "minute value 99 out of range" in output


def test_format_text_includes_next_occurrences():
    dt = datetime(2024, 6, 3, 9, 0, tzinfo=timezone.utc)
    report = _valid_report(next_occurrences=[dt])
    output = format_text(report)
    assert "Next runs" in output
    assert "2024-06-03" in output


# ---------------------------------------------------------------------------
# format_json
# ---------------------------------------------------------------------------

def test_format_json_is_valid_json():
    report = _valid_report()
    raw = format_json(report)
    data = json.loads(raw)
    assert data["valid"] is True
    assert data["expression"] == "0 9 * * 1"


def test_format_json_occurrences_are_iso_strings():
    dt = datetime(2024, 6, 3, 9, 0, tzinfo=timezone.utc)
    report = _valid_report(next_occurrences=[dt])
    data = json.loads(format_json(report))
    assert len(data["next_occurrences"]) == 1
    assert "2024-06-03T09:00:00" in data["next_occurrences"][0]


# ---------------------------------------------------------------------------
# build_report (integration)
# ---------------------------------------------------------------------------

def test_build_report_valid_expression():
    now = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    report = build_report("*/5 * * * *", timezone="UTC", count=3, now=now)
    assert report.is_valid
    assert len(report.next_occurrences) == 3
    assert report.explanation is not None


def test_build_report_invalid_expression():
    report = build_report("99 * * * *", timezone="UTC")
    assert not report.is_valid
    assert len(report.errors) > 0
    assert report.next_occurrences == []


def test_build_report_invalid_timezone():
    now = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)
    report = build_report("0 * * * *", timezone="Not/AZone", count=1, now=now)
    assert not report.is_valid
    assert any("timezone" in e.lower() or "zone" in e.lower() for e in report.errors)
