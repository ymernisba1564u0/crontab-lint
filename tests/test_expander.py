"""Tests for crontab_lint.expander."""

from __future__ import annotations

import pytest

from crontab_lint.expander import expand, ExpandResult


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _expand(expr: str) -> ExpandResult:
    return expand(expr)


# ---------------------------------------------------------------------------
# basic structure
# ---------------------------------------------------------------------------

def test_returns_expand_result():
    result = _expand("* * * * *")
    assert isinstance(result, ExpandResult)


def test_invalid_expression_not_valid():
    result = _expand("not a cron")
    assert result.valid is False


def test_invalid_expression_has_errors():
    result = _expand("not a cron")
    assert len(result.errors) > 0


def test_invalid_expression_has_empty_tuples():
    result = _expand("not a cron")
    assert result.tuples == []


def test_expression_preserved():
    expr = "0 12 * * 1"
    result = _expand(expr)
    assert result.expression == expr


# ---------------------------------------------------------------------------
# tuple counts
# ---------------------------------------------------------------------------

def test_every_minute_tuple_count():
    # 60 minutes * 24 hours * 31 doms * 12 months * 7 dows
    result = _expand("* * * * *")
    expected = 60 * 24 * 31 * 12 * 7
    assert len(result.tuples) == expected


def test_specific_minute_and_hour():
    # 1 minute * 1 hour * 31 * 12 * 7
    result = _expand("30 6 * * *")
    assert len(result.tuples) == 1 * 1 * 31 * 12 * 7


def test_specific_dow_reduces_count():
    # dow=1 only → 7 dows becomes 1
    result = _expand("0 9 * * 1")
    assert len(result.tuples) == 1 * 1 * 31 * 12 * 1


def test_step_in_minutes():
    # */15 → 0,15,30,45 → 4 values
    result = _expand("*/15 * * * *")
    assert len(result.tuples) == 4 * 24 * 31 * 12 * 7


def test_range_in_hours():
    # 9-11 → 3 values
    result = _expand("0 9-11 * * *")
    assert len(result.tuples) == 1 * 3 * 31 * 12 * 7


def test_list_in_months():
    # 1,6,12 → 3 months
    result = _expand("0 0 1 1,6,12 *")
    assert len(result.tuples) == 1 * 1 * 1 * 3 * 7


# ---------------------------------------------------------------------------
# tuple content
# ---------------------------------------------------------------------------

def test_tuple_structure_is_five_ints():
    result = _expand("5 4 3 2 1")
    assert result.valid
    t = result.tuples[0]
    assert len(t) == 5
    assert all(isinstance(v, int) for v in t)


def test_specific_values_appear_in_tuples():
    result = _expand("5 4 3 2 1")
    assert result.valid
    # minute=5, hour=4, dom=3, month=2, dow=1
    assert (5, 4, 3, 2, 1) in result.tuples


def test_valid_flag_true_for_valid_expression():
    result = _expand("* * * * *")
    assert result.valid is True


def test_errors_empty_for_valid_expression():
    result = _expand("0 0 * * *")
    assert result.errors == []
