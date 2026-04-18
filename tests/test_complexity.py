"""Tests for crontab_lint.complexity."""
import pytest
from crontab_lint.complexity import complexity, _level


def test_every_minute_is_simple():
    r = complexity("* * * * *")
    assert r.valid
    assert r.level == "simple"
    assert r.score == 0


def test_specific_time_moderate():
    r = complexity("30 9 * * *")
    assert r.valid
    # minute=1, hour=1
    assert r.score == 2
    assert r.level == "simple"


def test_list_increases_score():
    r = complexity("0,15,30,45 * * * *")
    assert r.valid
    assert r.score >= 4


def test_step_value_detected():
    r = complexity("*/15 * * * *")
    assert r.valid
    assert any("step" in reason for reason in r.reasons)


def test_range_detected():
    r = complexity("0 9-17 * * *")
    assert r.valid
    assert any("range" in reason for reason in r.reasons)


def test_complex_expression():
    r = complexity("0,30 8-18 * 1,6,12 1-5")
    assert r.valid
    assert r.level == "complex"


def test_invalid_expression_returns_invalid():
    r = complexity("bad expr")
    assert not r.valid
    assert r.score == -1
    assert r.level == "unknown"


def test_reasons_include_field_name():
    r = complexity("*/5 * * * *")
    assert any("minute" in reason for reason in r.reasons)


def test_level_boundaries():
    assert _level(0) == "simple"
    assert _level(2) == "simple"
    assert _level(3) == "moderate"
    assert _level(6) == "moderate"
    assert _level(7) == "complex"


def test_expression_preserved():
    expr = "0 12 * * 1"
    r = complexity(expr)
    assert r.expression == expr
