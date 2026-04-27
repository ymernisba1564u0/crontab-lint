"""Tests for crontab_lint.tracer."""
from datetime import datetime, timezone

import pytest

from crontab_lint.tracer import TraceResult, trace


UTC = timezone.utc


def _dt(year, month, day, hour, minute):
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


# ---------------------------------------------------------------------------
# Basic result structure
# ---------------------------------------------------------------------------

def test_returns_trace_result():
    result = trace("* * * * *", count=3, before=_dt(2024, 6, 1, 12, 0))
    assert isinstance(result, TraceResult)


def test_valid_expression_is_valid():
    result = trace("* * * * *", count=1, before=_dt(2024, 6, 1, 12, 0))
    assert result.valid is True


def test_invalid_expression_is_not_valid():
    result = trace("99 * * * *", count=1)
    assert result.valid is False


def test_invalid_expression_has_errors():
    result = trace("99 * * * *", count=1)
    assert len(result.errors) > 0


def test_invalid_expression_has_empty_occurrences():
    result = trace("99 * * * *", count=1)
    assert result.occurrences == []


# ---------------------------------------------------------------------------
# Occurrence count
# ---------------------------------------------------------------------------

def test_every_minute_returns_correct_count():
    result = trace("* * * * *", count=5, before=_dt(2024, 6, 1, 12, 0))
    assert len(result.occurrences) == 5


def test_count_clamped_to_minimum_one():
    result = trace("* * * * *", count=0, before=_dt(2024, 6, 1, 12, 0))
    assert len(result.occurrences) == 1


def test_count_clamped_to_maximum_100():
    result = trace("* * * * *", count=200, before=_dt(2024, 6, 1, 12, 0))
    assert len(result.occurrences) == 100


# ---------------------------------------------------------------------------
# Ordering and values
# ---------------------------------------------------------------------------

def test_occurrences_are_in_descending_order():
    result = trace("* * * * *", count=3, before=_dt(2024, 6, 1, 12, 0))
    times = result.occurrences
    assert times[0] > times[1] > times[2]


def test_occurrences_are_before_reference_time():
    ref = _dt(2024, 6, 1, 12, 0)
    result = trace("* * * * *", count=5, before=ref)
    for occ in result.occurrences:
        assert occ < ref


def test_specific_minute_only_returns_that_minute():
    # "30 * * * *" fires at :30 of every hour
    ref = _dt(2024, 6, 1, 15, 0)  # 15:00, so last fire was 14:30
    result = trace("30 * * * *", count=3, before=ref)
    for occ in result.occurrences:
        assert occ.minute == 30


def test_specific_time_daily_interval():
    # "0 9 * * *" fires at 09:00 every day
    ref = _dt(2024, 6, 5, 10, 0)
    result = trace("0 9 * * *", count=3, before=ref)
    assert len(result.occurrences) == 3
    for occ in result.occurrences:
        assert occ.hour == 9
        assert occ.minute == 0


# ---------------------------------------------------------------------------
# Timezone awareness
# ---------------------------------------------------------------------------

def test_occurrences_are_timezone_aware():
    result = trace("* * * * *", count=2, before=_dt(2024, 6, 1, 12, 0))
    for occ in result.occurrences:
        assert occ.tzinfo is not None


def test_expression_preserved_in_result():
    expr = "0 6 * * 1"
    result = trace(expr, count=1, before=_dt(2024, 6, 10, 7, 0))
    assert result.expression == expr


def test_timezone_preserved_in_result():
    result = trace("* * * * *", tz_name="Europe/London", count=1,
                   before=_dt(2024, 6, 1, 12, 0))
    assert result.timezone == "Europe/London"


def test_invalid_timezone_returns_error():
    result = trace("* * * * *", tz_name="Not/AZone", count=1)
    assert result.valid is False
    assert result.errors
