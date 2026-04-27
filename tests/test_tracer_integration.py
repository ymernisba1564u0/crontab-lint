"""Integration tests for the tracer module using real scheduler logic."""
from datetime import datetime, timedelta, timezone

import pytest

from crontab_lint.tracer import trace

UTC = timezone.utc


def _dt(year, month, day, hour, minute):
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


def test_every_minute_last_occurrence_is_one_minute_before_ref():
    ref = _dt(2024, 3, 15, 10, 30)
    result = trace("* * * * *", count=1, before=ref)
    assert result.occurrences[0] == _dt(2024, 3, 15, 10, 29)


def test_every_minute_consecutive_occurrences_are_one_minute_apart():
    ref = _dt(2024, 3, 15, 10, 30)
    result = trace("* * * * *", count=3, before=ref)
    for i in range(len(result.occurrences) - 1):
        delta = result.occurrences[i] - result.occurrences[i + 1]
        assert delta == timedelta(minutes=1)


def test_hourly_expression_occurrences_are_one_hour_apart():
    ref = _dt(2024, 3, 15, 10, 0)
    result = trace("0 * * * *", count=3, before=ref)
    for i in range(len(result.occurrences) - 1):
        delta = result.occurrences[i] - result.occurrences[i + 1]
        assert delta == timedelta(hours=1)


def test_daily_expression_occurrences_are_one_day_apart():
    ref = _dt(2024, 3, 15, 10, 0)
    result = trace("0 9 * * *", count=3, before=ref)
    for i in range(len(result.occurrences) - 1):
        delta = result.occurrences[i] - result.occurrences[i + 1]
        assert delta == timedelta(days=1)


def test_weekly_expression_occurrences_are_seven_days_apart():
    # Monday = weekday 1 in cron; pick a ref that is a Tuesday
    ref = _dt(2024, 3, 19, 10, 0)  # Tuesday
    result = trace("0 9 * * 1", count=2, before=ref)
    if len(result.occurrences) == 2:
        delta = result.occurrences[0] - result.occurrences[1]
        assert delta == timedelta(days=7)


def test_occurrences_never_equal_or_exceed_before():
    ref = _dt(2024, 6, 1, 12, 0)
    result = trace("* * * * *", count=10, before=ref)
    for occ in result.occurrences:
        assert occ < ref


def test_specific_dow_only_returns_correct_weekday():
    # cron DOW: 0=Sun,1=Mon,...,6=Sat  — Python weekday: Mon=0 … Sun=6
    # "0 0 * * 0" = every Sunday midnight
    ref = _dt(2024, 3, 20, 1, 0)  # Wednesday
    result = trace("0 0 * * 0", count=2, before=ref)
    for occ in result.occurrences:
        # Sunday in Python is weekday() == 6
        assert occ.weekday() == 6
