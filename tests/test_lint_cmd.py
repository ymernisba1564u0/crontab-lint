"""Tests for the lint command handler."""
from __future__ import annotations

import json
import types
from io import StringIO

import pytest

from crontab_lint.commands.lint_cmd import handle


def _ns(**kwargs):
    defaults = dict(
        expressions=["* * * * *"],
        timezone="UTC",
        count=3,
        output_format="text",
    )
    defaults.update(kwargs)
    return types.SimpleNamespace(**defaults)


def test_valid_expression_returns_zero():
    out = StringIO()
    rc = handle(_ns(), out=out)
    assert rc == 0


def test_invalid_expression_returns_one():
    out = StringIO()
    rc = handle(_ns(expressions=["99 * * * *"]), out=out)
    assert rc == 1


def test_text_output_contains_checkmark():
    out = StringIO()
    handle(_ns(), out=out)
    assert "✔" in out.getvalue()


def test_text_output_contains_cross_for_invalid():
    out = StringIO()
    handle(_ns(expressions=["99 * * * *"]), out=out)
    assert "✘" in out.getvalue()


def test_json_output_is_valid_json():
    out = StringIO()
    handle(_ns(output_format="json"), out=out)
    data = json.loads(out.getvalue())
    assert isinstance(data, list)
    assert len(data) == 1


def test_json_output_multiple_expressions():
    out = StringIO()
    exprs = ["* * * * *", "0 9 * * 1"]
    handle(_ns(expressions=exprs, output_format="json"), out=out)
    data = json.loads(out.getvalue())
    assert len(data) == 2


def test_mixed_validity_returns_one():
    out = StringIO()
    rc = handle(_ns(expressions=["* * * * *", "99 * * * *"]), out=out)
    assert rc == 1


def test_next_occurrences_count_respected():
    out = StringIO()
    handle(_ns(output_format="json", count=2), out=out)
    data = json.loads(out.getvalue())
    assert len(data[0]["next_occurrences"]) == 2
