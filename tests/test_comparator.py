"""Tests for crontab_lint.comparator."""
import pytest
from crontab_lint.comparator import compare


def test_identical_expressions_are_equivalent():
    result = compare("0 9 * * 1", "0 9 * * 1")
    assert result.are_equivalent is True


def test_alias_and_numeric_equivalent():
    result = compare("0 9 * * MON", "0 9 * * 1")
    assert result.are_equivalent is True


def test_different_expressions_not_equivalent():
    result = compare("0 9 * * 1", "0 10 * * 1")
    assert result.are_equivalent is False


def test_both_valid_set_for_valid_expressions():
    result = compare("0 9 * * *", "0 9 * * *")
    assert result.both_valid is True


def test_both_valid_false_when_first_invalid():
    result = compare("invalid", "0 9 * * *")
    assert result.both_valid is False
    assert result.are_equivalent is False


def test_both_valid_false_when_second_invalid():
    result = compare("0 9 * * *", "bad expr")
    assert result.both_valid is False


def test_errors_populated_for_invalid_expression():
    result = compare("bad", "0 9 * * *")
    assert len(result.errors_a) > 0


def test_normalized_fields_returned():
    result = compare("0 9 * * MON", "0 9 * * 1")
    assert result.normalized_a == result.normalized_b


def test_month_alias_equivalence():
    result = compare("0 0 1 JAN *", "0 0 1 1 *")
    assert result.are_equivalent is True


def test_expression_fields_preserved():
    result = compare("* * * * *", "0 9 * * *")
    assert result.expression_a == "* * * * *"
    assert result.expression_b == "0 9 * * *"
