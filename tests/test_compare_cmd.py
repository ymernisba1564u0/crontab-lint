"""Tests for crontab_lint.commands.compare_cmd."""
import argparse
import json
from io import StringIO
from unittest import mock
import pytest
from crontab_lint.commands.compare_cmd import handle, _format_text
from crontab_lint.comparator import compare


def _ns(expr_a, expr_b, fmt="text"):
    return argparse.Namespace(expression_a=expr_a, expression_b=expr_b, format=fmt)


def test_equivalent_returns_zero():
    assert handle(_ns("0 9 * * MON", "0 9 * * 1")) == 0


def test_not_equivalent_returns_one():
    assert handle(_ns("0 9 * * *", "0 10 * * *")) == 1


def test_invalid_expression_returns_one():
    assert handle(_ns("bad", "0 9 * * *")) == 1


def test_text_shows_equivalent(capsys):
    handle(_ns("* * * * *", "* * * * *"))
    out = capsys.readouterr().out
    assert "equivalent" in out
    assert "✔" in out


def test_text_shows_not_equivalent(capsys):
    handle(_ns("0 9 * * *", "0 10 * * *"))
    out = capsys.readouterr().out
    assert "not equivalent" in out


def test_text_shows_invalid(capsys):
    handle(_ns("bad", "0 9 * * *"))
    out = capsys.readouterr().out
    assert "invalid" in out


def test_json_output_is_valid_json(capsys):
    handle(_ns("* * * * *", "* * * * *", fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "are_equivalent" in data


def test_json_both_valid_field(capsys):
    handle(_ns("0 9 * * *", "0 9 * * *", fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["both_valid"] is True


def test_json_errors_present_for_invalid(capsys):
    handle(_ns("bad", "0 9 * * *", fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert len(data["errors_a"]) > 0
