"""Tests for crontab_lint.conflict."""
import pytest
from crontab_lint.conflict import find_conflicts, ConflictResult


def test_returns_conflict_result():
    result = find_conflicts(["* * * * *", "*/2 * * * *"])
    assert isinstance(result, ConflictResult)


def test_identical_expressions_have_conflicts():
    result = find_conflicts(["0 9 * * *", "0 9 * * *"], count=5)
    assert result.total_conflicts > 0


def test_non_overlapping_expressions_no_conflicts():
    # one fires at minute 1, other at minute 2 — no overlap in a small window
    result = find_conflicts(["1 0 1 1 *", "2 0 1 1 *"], count=5)
    assert result.total_conflicts == 0


def test_conflict_tuple_structure():
    result = find_conflicts(["0 12 * * *", "0 12 * * *"], count=3)
    for item in result.conflicts:
        assert len(item) == 3
        a, b, ts = item
        assert isinstance(a, str)
        assert isinstance(b, str)
        assert isinstance(ts, str)


def test_expressions_preserved():
    exprs = ["* * * * *", "0 * * * *"]
    result = find_conflicts(exprs, count=10)
    assert result.expressions == exprs


def test_checked_occurrences_preserved():
    result = find_conflicts(["* * * * *"], count=20)
    assert result.checked_occurrences == 20


def test_invalid_expression_does_not_crash():
    result = find_conflicts(["invalid", "* * * * *"], count=5)
    assert isinstance(result, ConflictResult)


def test_single_expression_no_conflicts():
    result = find_conflicts(["0 6 * * *"], count=5)
    assert result.total_conflicts == 0
