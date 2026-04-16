"""Unit tests for crontab_lint.explainer."""
from __future__ import annotations

import pytest

from crontab_lint.parser import parse
from crontab_lint.explainer import explain, _explain_field


def _parse(expr: str):
    result = parse(expr)
    assert result.ok, result.errors
    return result


def test_explain_every_minute():
    text = explain(_parse("* * * * *"))
    assert "every minute" in text.lower()


def test_explain_specific_hour_and_minute():
    text = explain(_parse("30 9 * * *"))
    assert "09:30" in text or "9" in text


def test_explain_returns_string():
    text = explain(_parse("*/15 * * * *"))
    assert isinstance(text, str)
    assert len(text) > 0


def test_explain_step_in_minutes():
    text = explain(_parse("*/10 * * * *"))
    assert "10" in text


def test_explain_field_wildcard():
    result = _explain_field("*", "minute")
    assert "every" in result.lower() or result == "*"


def test_explain_field_specific():
    result = _explain_field("5", "minute")
    assert "5" in result


def test_explain_monthly():
    text = explain(_parse("0 0 1 * *"))
    assert any(word in text.lower() for word in ["1st", "day", "month", "1"])


def test_explain_weekday():
    text = explain(_parse("0 8 * * 1"))
    assert any(word in text.lower() for word in ["monday", "mon", "weekday", "1"])


def test_explain_alias_month():
    text = explain(_parse("0 0 * JAN *"))
    assert any(word in text.lower() for word in ["jan", "1", "january"])


def test_explain_range():
    text = explain(_parse("0 9-17 * * *"))
    assert "9" in text and "17" in text
