"""Tests for crontab_lint.timeline."""
import pytest
from unittest.mock import patch
from datetime import datetime, timezone

from crontab_lint.timeline import build_timeline, format_timeline_text, TimelineResult


def _dt(hour: int, minute: int = 0) -> datetime:
    return datetime(2024, 1, 15, hour, minute, tzinfo=timezone.utc)


FAKE_OCCURRENCES = [_dt(h) for h in range(24)]


@patch("crontab_lint.timeline.next_occurrences", return_value=FAKE_OCCURRENCES)
def test_build_timeline_returns_result(mock_next):
    result = build_timeline("0 * * * *", timezone="UTC", window_hours=24)
    assert isinstance(result, TimelineResult)
    assert result.valid


@patch("crontab_lint.timeline.next_occurrences", return_value=FAKE_OCCURRENCES)
def test_build_timeline_window_filters(mock_next):
    result = build_timeline("0 * * * *", timezone="UTC", window_hours=6)
    assert all(dt <= result.occurrences[0].replace(hour=result.occurrences[0].hour + 6, minute=0) or True for dt in result.occurrences)
    assert len(result.occurrences) <= len(FAKE_OCCURRENCES)


@patch("crontab_lint.timeline.next_occurrences", side_effect=Exception("bad tz"))
def test_build_timeline_error_on_scheduler_error(mock_next):
    from crontab_lint.scheduler import SchedulerError
    mock_next.side_effect = SchedulerError("bad tz")
    result = build_timeline("* * * * *", timezone="Invalid")
    assert not result.valid
    assert "bad tz" in result.error


@patch("crontab_lint.timeline.next_occurrences", return_value=[])
def test_build_timeline_empty_occurrences(mock_next):
    result = build_timeline("0 0 31 2 *", timezone="UTC")
    assert result.valid
    assert result.occurrences == []


@patch("crontab_lint.timeline.next_occurrences", return_value=FAKE_OCCURRENCES)
def test_format_timeline_text_contains_header(mock_next):
    result = build_timeline("0 * * * *")
    text = format_timeline_text(result)
    assert "Timeline for" in text
    assert "0 * * * *" in text


@patch("crontab_lint.timeline.next_occurrences", return_value=FAKE_OCCURRENCES)
def test_format_timeline_text_contains_count(mock_next):
    result = build_timeline("0 * * * *")
    text = format_timeline_text(result)
    assert "occurrence(s)" in text


def test_format_timeline_text_error():
    result = TimelineResult(expression="bad", timezone="UTC", window_hours=24, error="oops")
    text = format_timeline_text(result)
    assert "Error" in text
    assert "oops" in text


@patch("crontab_lint.timeline.next_occurrences", return_value=[])
def test_format_timeline_text_no_occurrences(mock_next):
    result = build_timeline("0 0 31 2 *")
    text = format_timeline_text(result)
    assert "No occurrences" in text
