"""Tests for crontab_lint.differ."""

import pytest
from crontab_lint.differ import diff, DiffResult


def test_equivalent_expressions_have_no_diffs():
    result = diff("0 9 * * 1", "0 9 * * 1")
    assert result.field_diffs == []
    assert result.summary == "Expressions are equivalent."


def test_different_minute_detected():
    result = diff("0 9 * * 1", "30 9 * * 1")
    assert any("minute" in d for d in result.field_diffs)


def test_multiple_field_diffs_counted():
    result = diff("0 9 * * 1", "30 18 * * 5")
    assert len(result.field_diffs) == 3
    assert "3 field(s) differ." in result.summary


def test_both_valid_flags_set_for_valid_expressions():
    result = diff("* * * * *", "0 0 * * *")
    assert result.valid_a is True
    assert result.valid_b is True


def test_invalid_first_expression():
    result = diff("99 * * * *", "0 0 * * *")
    assert result.valid_a is False
    assert result.valid_b is True
    assert result.summary == "First expression is invalid."


def test_invalid_second_expression():
    result = diff("0 0 * * *", "* * * * 9")
    assert result.valid_a is True
    assert result.valid_b is False
    assert result.summary == "Second expression is invalid."


def test_both_invalid():
    result = diff("99 * * * *", "* * * * 9")
    assert result.valid_a is False
    assert result.valid_b is False
    assert result.summary == "Both expressions are invalid."


def test_explanations_present_for_valid():
    result = diff("0 9 * * *", "0 17 * * *")
    assert len(result.explanation_a) > 0
    assert len(result.explanation_b) > 0


def test_explanation_shows_invalid_message_for_bad_expr():
    result = diff("99 * * * *", "0 0 * * *")
    assert "Invalid" in result.explanation_a


def test_expressions_preserved_in_result():
    result = diff("0 9 * * 1", "0 10 * * 1")
    assert result.expression_a == "0 9 * * 1"
    assert result.expression_b == "0 10 * * 1"


def test_single_field_diff_summary():
    """A single differing field should use singular phrasing in the summary."""
    result = diff("0 9 * * 1", "0 10 * * 1")
    assert len(result.field_diffs) == 1
    assert "1 field(s) differ." in result.summary
