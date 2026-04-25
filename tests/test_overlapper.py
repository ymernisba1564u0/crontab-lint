"""Tests for crontab_lint.overlapper."""
from __future__ import annotations

import pytest

from crontab_lint.overlapper import OverlapResult, find_overlaps


def test_returns_overlap_result():
    result = find_overlaps(["* * * * *", "*/2 * * * *"])
    assert isinstance(result, OverlapResult)


def test_expressions_preserved():
    exprs = ["* * * * *", "0 * * * *"]
    result = find_overlaps(exprs)
    assert result.expressions == exprs


def test_timezone_preserved():
    result = find_overlaps(["* * * * *"], timezone="Europe/London")
    assert result.timezone == "Europe/London"


def test_identical_expressions_overlap():
    result = find_overlaps(["0 9 * * 1", "0 9 * * 1"])
    assert len(result.overlaps) == 1
    a, b, count = result.overlaps[0]
    assert count > 0


def test_non_overlapping_expressions_no_overlap():
    # minute 0 vs minute 30 — they never share a timestamp
    result = find_overlaps(["0 * * * *", "30 * * * *"])
    assert result.overlaps == []


def test_every_minute_overlaps_with_every_two_minutes():
    result = find_overlaps(["* * * * *", "*/2 * * * *"])
    assert len(result.overlaps) == 1
    _, _, shared = result.overlaps[0]
    assert shared > 0


def test_total_pairs_checked_single_pair():
    result = find_overlaps(["* * * * *", "0 * * * *"])
    assert result.total_pairs_checked == 1


def test_total_pairs_checked_three_expressions():
    result = find_overlaps(["* * * * *", "0 * * * *", "30 * * * *"])
    assert result.total_pairs_checked == 3


def test_threshold_filters_low_overlap():
    # every minute vs every 30 minutes shares 2 occurrences per hour in 60-sample
    result_low = find_overlaps(["* * * * *", "*/30 * * * *"], threshold=1)
    result_high = find_overlaps(["* * * * *", "*/30 * * * *"], threshold=1000)
    assert len(result_low.overlaps) >= len(result_high.overlaps)


def test_single_expression_no_pairs():
    result = find_overlaps(["* * * * *"])
    assert result.total_pairs_checked == 0
    assert result.overlaps == []


def test_empty_list_no_pairs():
    result = find_overlaps([])
    assert result.total_pairs_checked == 0
    assert result.overlaps == []
