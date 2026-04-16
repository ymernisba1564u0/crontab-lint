"""Tests for crontab_lint.normalizer."""
import pytest
from crontab_lint.normalizer import normalize


def test_no_change_for_numeric_expression():
    r = normalize("0 9 * * *")
    assert r.normalized == "0 9 * * *"
    assert not r.changed


def test_month_alias_lowered():
    r = normalize("0 0 1 JAN *")
    assert "JAN" not in r.normalized
    assert r.normalized == "0 0 1 1 *"
    assert r.changed


def test_dow_alias_lowered():
    r = normalize("0 8 * * MON")
    assert r.normalized == "0 8 * * 1"
    assert r.changed


def test_mixed_aliases():
    r = normalize("30 6 * DEC FRI")
    assert r.normalized == "30 6 * 12 5"
    assert r.changed


def test_lowercase_alias():
    r = normalize("0 0 * feb *")
    assert r.normalized == "0 0 * 2 *"
    assert r.changed


def test_invalid_expression_returns_error():
    r = normalize("bad expression")
    assert r.error is not None
    assert not r.changed
    assert r.normalized == "bad expression"


def test_parse_result_attached_for_valid():
    r = normalize("*/5 * * * *")
    assert r.parse_result is not None
    assert r.parse_result.valid


def test_original_preserved():
    expr = "0 12 * JAN *"
    r = normalize(expr)
    assert r.original == expr


def test_wildcard_fields_unchanged():
    r = normalize("* * * * *")
    assert r.normalized == "* * * * *"
    assert not r.changed
