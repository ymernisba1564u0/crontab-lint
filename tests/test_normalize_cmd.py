"""Tests for the normalize sub-command."""
import argparse
import json
from unittest.mock import patch
import pytest

from crontab_lint.commands.normalize_cmd import handle


def _ns(expression: str, fmt: str = "text") -> argparse.Namespace:
    return argparse.Namespace(expression=expression, fmt=fmt)


def test_valid_numeric_returns_zero():
    with patch("builtins.print"):
        assert handle(_ns("0 9 * * *")) == 0


def test_invalid_expression_returns_one():
    with patch("builtins.print"):
        assert handle(_ns("not valid at all")) == 1


def test_text_shows_original_and_normalized(capsys):
    handle(_ns("0 0 1 JAN *"))
    out = capsys.readouterr().out
    assert "0 0 1 JAN *" in out
    assert "0 0 1 1 *" in out


def test_text_shows_changed_flag(capsys):
    handle(_ns("0 8 * * MON"))
    out = capsys.readouterr().out
    assert "changed" in out


def test_text_shows_no_changes_needed(capsys):
    handle(_ns("*/5 * * * *"))
    out = capsys.readouterr().out
    assert "no changes needed" in out


def test_json_output_is_valid_json(capsys):
    handle(_ns("0 0 * DEC FRI", fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert isinstance(data, dict)


def test_json_changed_field(capsys):
    handle(_ns("0 0 * DEC FRI", fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["changed"] is True
    assert data["normalized"] == "0 0 * 12 5"


def test_json_valid_field_false_for_invalid(capsys):
    handle(_ns("bad expr", fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["valid"] is False
    assert data["error"] is not None
