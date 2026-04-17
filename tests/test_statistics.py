"""Tests for crontab_lint.statistics."""
import pytest
from crontab_lint.statistics import compute, StatisticsReport

VALID = ["* * * * *", "0 9 * * 1", "30 6 * * *", "0 9 * * 2"]
INVALID = ["invalid", "99 * * * *"]


def test_total_count():
    report = compute(VALID)
    assert report.total == len(VALID)


def test_valid_count():
    report = compute(VALID)
    assert report.valid_count == len(VALID)


def test_invalid_count():
    report = compute(INVALID)
    assert report.invalid_count == len(INVALID)


def test_mixed_valid_invalid():
    report = compute(VALID + INVALID)
    assert report.valid_count == len(VALID)
    assert report.invalid_count == len(INVALID)


def test_error_messages_populated_for_invalid():
    report = compute(INVALID)
    assert len(report.error_messages) > 0


def test_error_messages_empty_for_all_valid():
    report = compute(VALID)
    assert report.error_messages == []


def test_most_common_hours_type():
    report = compute(VALID)
    assert isinstance(report.most_common_hours, list)


def test_most_common_minutes_respects_top_n():
    report = compute(VALID, top_n=2)
    assert len(report.most_common_minutes) <= 2


def test_hour_9_is_most_common():
    report = compute(VALID)
    top_hours = [h for h, _ in report.most_common_hours]
    assert "9" in top_hours


def test_empty_input():
    report = compute([])
    assert report.total == 0
    assert report.valid_count == 0
    assert report.invalid_count == 0


def test_warning_count_is_int():
    report = compute(VALID)
    assert isinstance(report.warning_count, int)
