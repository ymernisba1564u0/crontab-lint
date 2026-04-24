"""Tests for crontab_lint.frequency."""
import pytest
from crontab_lint.frequency import frequency, FrequencyResult


def test_returns_frequency_result():
    result = frequency("* * * * *")
    assert isinstance(result, FrequencyResult)


def test_every_minute_is_valid():
    result = frequency("* * * * *")
    assert result.valid is True
    assert result.errors == []


def test_invalid_expression_not_valid():
    result = frequency("99 * * * *")
    assert result.valid is False


def test_invalid_expression_has_no_runs():
    result = frequency("99 * * * *")
    assert result.runs_per_day is None
    assert result.runs_per_hour is None
    assert result.runs_per_week is None
    assert result.runs_per_month is None


def test_invalid_expression_has_no_label():
    result = frequency("99 * * * *")
    assert result.label is None


def test_every_minute_label():
    result = frequency("* * * * *")
    assert result.label == "every minute"


def test_every_minute_runs_per_hour():
    result = frequency("* * * * *")
    assert result.runs_per_hour > 1


def test_daily_expression_label():
    # Runs once a day at midnight
    result = frequency("0 0 * * *")
    assert result.label == "daily"


def test_daily_expression_runs_per_day():
    result = frequency("0 0 * * *")
    assert 0.9 <= result.runs_per_day <= 1.1


def test_hourly_expression_label():
    result = frequency("0 * * * *")
    assert result.label in ("every hour or more", "multiple times a day")


def test_weekly_expression_label():
    # Once a week on Sunday midnight
    result = frequency("0 0 * * 0")
    assert result.label == "weekly"


def test_step_minute_reduces_frequency():
    every_minute = frequency("* * * * *")
    every_five = frequency("*/5 * * * *")
    assert every_five.runs_per_day < every_minute.runs_per_day


def test_expression_preserved():
    expr = "30 6 * * 1-5"
    result = frequency(expr)
    assert result.expression == expr


def test_runs_per_week_greater_than_runs_per_day():
    result = frequency("*/10 * * * *")
    assert result.runs_per_week > result.runs_per_day


def test_runs_per_month_greater_than_runs_per_week():
    result = frequency("*/10 * * * *")
    assert result.runs_per_month > result.runs_per_week


def test_invalid_expression_errors_populated():
    result = frequency("abc * * * *")
    assert len(result.errors) > 0
