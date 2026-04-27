"""Tests for crontab_lint.commands.trace_cmd."""
import argparse
import json
from datetime import datetime, timezone
from io import StringIO
from unittest.mock import patch

import pytest

from crontab_lint.commands.trace_cmd import handle, _format_text
from crontab_lint.tracer import TraceResult


_BEFORE = datetime(2024, 6, 1, 12, 0, tzinfo=timezone.utc)


def _ns(**kwargs):
    defaults = dict(
        expression="* * * * *",
        timezone="UTC",
        count=5,
        before=None,
        output_format="text",
    )
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _valid_result(expr="* * * * *", n=3):
    from crontab_lint.tracer import trace
    return trace(expr, count=n, before=_BEFORE)


# ---------------------------------------------------------------------------
# Return codes
# ---------------------------------------------------------------------------

def test_valid_expression_returns_zero(capsys):
    ns = _ns(expression="* * * * *", count=3)
    code = handle(ns)
    assert code == 0


def test_invalid_expression_returns_one(capsys):
    ns = _ns(expression="99 * * * *", count=1)
    code = handle(ns)
    assert code == 1


def test_bad_before_returns_two(capsys):
    ns = _ns(before="not-a-date")
    code = handle(ns)
    assert code == 2


# ---------------------------------------------------------------------------
# Text output
# ---------------------------------------------------------------------------

def test_text_output_contains_checkmark(capsys):
    handle(_ns(expression="* * * * *", count=2))
    out = capsys.readouterr().out
    assert "\u2714" in out


def test_text_output_contains_cross_for_invalid(capsys):
    handle(_ns(expression="99 * * * *"))
    out = capsys.readouterr().out
    assert "\u2718" in out


def test_text_output_contains_occurrences(capsys):
    handle(_ns(expression="* * * * *", count=3))
    out = capsys.readouterr().out
    assert "occurrence" in out.lower()


# ---------------------------------------------------------------------------
# JSON output
# ---------------------------------------------------------------------------

def test_json_output_is_valid_json(capsys):
    handle(_ns(expression="* * * * *", count=2, output_format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, dict)


def test_json_output_has_occurrences_key(capsys):
    handle(_ns(expression="* * * * *", count=2, output_format="json"))
    data = json.loads(capsys.readouterr().out)
    assert "occurrences" in data


def test_json_output_valid_flag(capsys):
    handle(_ns(expression="* * * * *", count=1, output_format="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["valid"] is True


def test_json_invalid_has_errors(capsys):
    handle(_ns(expression="99 * * * *", output_format="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["valid"] is False
    assert len(data["errors"]) > 0


# ---------------------------------------------------------------------------
# _format_text helper
# ---------------------------------------------------------------------------

def test_format_text_valid_shows_expression():
    result = _valid_result()
    text = _format_text(result)
    assert "* * * * *" in text


def test_format_text_invalid_shows_errors():
    from crontab_lint.tracer import trace
    result = trace("99 * * * *", count=1)
    text = _format_text(result)
    assert "Invalid" in text or len(result.errors) > 0
