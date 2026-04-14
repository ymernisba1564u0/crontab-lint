"""Tests for crontab_lint.scheduler."""

from datetime import datetime, timezone

import pytest

try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo  # type: ignore

from crontab_lint.scheduler import SchedulerError, next_occurrences

UTC = timezone.utc
ANCHOR = datetime(2024, 3, 15, 12, 0, 0, tzinfo=UTC)  # Friday


def test_every_minute_returns_correct_count():
    results = next_occurrences("* * * * *", count=5, after=ANCHOR)
    assert len(results) == 5


def test_every_minute_increments_by_one_minute():
    results = next_occurrences("* * * * *", count=3, after=ANCHOR)
    for i in range(1, len(results)):
        delta = results[i] - results[i - 1]
        assert delta.total_seconds() == 60


def test_specific_time_daily():
    results = next_occurrences("30 9 * * *", count=3, after=ANCHOR)
    for dt in results:
        assert dt.hour == 9
        assert dt.minute == 30


def test_specific_time_daily_increments_by_one_day():
    results = next_occurrences("30 9 * * *", count=2, after=ANCHOR)
    delta = results[1] - results[0]
    assert delta.total_seconds() == 86400


def test_results_are_timezone_aware():
    results = next_occurrences("* * * * *", count=1, tz_name="America/New_York", after=ANCHOR)
    assert results[0].tzinfo is not None


def test_invalid_expression_raises():
    with pytest.raises(SchedulerError, match="Invalid cron expression"):
        next_occurrences("invalid expr", count=1, after=ANCHOR)


def test_unknown_timezone_raises():
    with pytest.raises(SchedulerError, match="Unknown timezone"):
        next_occurrences("* * * * *", count=1, tz_name="Mars/Olympus", after=ANCHOR)


def test_step_expression():
    results = next_occurrences("*/15 * * * *", count=4, after=ANCHOR)
    for dt in results:
        assert dt.minute % 15 == 0


def test_weekday_filter():
    # 1 = Monday in cron (0 or 7 = Sunday)
    results = next_occurrences("0 0 * * 1", count=3, after=ANCHOR)
    for dt in results:
        assert dt.weekday() == 0  # Python Monday == 0


def test_month_filter():
    results = next_occurrences("0 12 1 6 *", count=2, after=ANCHOR)
    for dt in results:
        assert dt.month == 6
        assert dt.day == 1
        assert dt.hour == 12
        assert dt.minute == 0
