"""Tests for the cron expression parser."""

import pytest
from crontab_lint.parser import parse


def test_valid_every_minute():
    result = parse("* * * * *")
    assert result.is_valid
    assert result.errors == []


def test_valid_specific_time():
    result = parse("30 14 * * *")
    assert result.is_valid
    assert result.errors == []


def test_valid_with_range():
    result = parse("0 9-17 * * 1-5")
    assert result.is_valid


def test_valid_with_step():
    result = parse("*/15 * * * *")
    assert result.is_valid


def test_valid_month_alias():
    result = parse("0 0 1 jan *")
    assert result.is_valid


def test_valid_dow_alias():
    result = parse("0 9 * * mon-fri")
    assert result.is_valid


def test_invalid_wrong_field_count():
    result = parse("* * *")
    assert not result.is_valid
    assert any("5 fields" in e for e in result.errors)


def test_invalid_minute_out_of_range():
    result = parse("60 * * * *")
    assert not result.is_valid
    assert any("minute" in e for e in result.errors)


def test_invalid_hour_out_of_range():
    result = parse("0 24 * * *")
    assert not result.is_valid
    assert any("hour" in e for e in result.errors)


def test_invalid_range_start_greater_than_end():
    result = parse("0 17-9 * * *")
    assert not result.is_valid
    assert any("start > end" in e for e in result.errors)


def test_invalid_step_zero():
    result = parse("*/0 * * * *")
    assert not result.is_valid
    assert any("zero" in e for e in result.errors)


def test_invalid_bad_token():
    result = parse("0 0 * * ?")
    assert not result.is_valid
    assert any("Invalid token" in e for e in result.errors)


def test_multiple_errors_collected():
    result = parse("99 25 * * *")
    assert not result.is_valid
    assert len(result.errors) >= 2


def test_comma_separated_valid():
    result = parse("0,15,30,45 * * * *")
    assert result.is_valid


def test_field_names_assigned_correctly():
    result = parse("5 10 15 6 3")
    assert result.fields[0].name == "minute"
    assert result.fields[1].name == "hour"
    assert result.fields[4].name == "day_of_week"
