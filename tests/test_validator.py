"""Tests for crontab_lint.validator."""

import pytest
from crontab_lint.validator import validate, ValidationResult


def test_valid_expression_is_valid():
    result = validate("0 9 * * 1-5")
    assert result.is_valid is True
    assert result.errors == []


def test_invalid_expression_is_not_valid():
    result = validate("99 9 * * *")
    assert result.is_valid is False
    assert len(result.errors) > 0


def test_invalid_expression_has_no_warnings():
    """Warnings should not be generated when parsing already failed."""
    result = validate("abc * * * *")
    assert result.is_valid is False
    assert result.warnings == []


def test_parse_result_attached_for_valid():
    result = validate("*/15 * * * *")
    assert result.parse_result is not None
    assert result.parse_result.is_valid is True


def test_parse_result_attached_for_invalid():
    result = validate("0 25 * * *")
    assert result.parse_result is not None
    assert result.parse_result.is_valid is False


def test_every_minute_warning():
    result = validate("* * * * *")
    assert result.is_valid is True
    assert any("every minute" in w.lower() for w in result.warnings)


def test_feb_30_warning():
    result = validate("0 0 30 2 *")
    assert result.is_valid is True
    assert any("february" in w.lower() for w in result.warnings)


def test_feb_29_warning():
    result = validate("0 0 29 2 *")
    assert result.is_valid is True
    assert any("leap" in w.lower() for w in result.warnings)


def test_day_31_warning():
    result = validate("0 0 31 * *")
    assert result.is_valid is True
    assert any("31" in w for w in result.warnings)


def test_no_spurious_warnings_for_normal_expression():
    result = validate("30 8 * * 1-5")
    assert result.is_valid is True
    assert result.warnings == []


def test_expression_preserved():
    expr = "5 4 * * sun"
    result = validate(expr)
    assert result.expression == expr


def test_returns_validation_result_instance():
    result = validate("0 0 * * *")
    assert isinstance(result, ValidationResult)
