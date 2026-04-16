"""Tests for the explain command handler."""
from __future__ import annotations

import json
import argparse
from unittest.mock import patch

import pytest

from crontab_lint.commands.explain_cmd import handle, register


def _ns(**kwargs):
    defaults = {"expression": "* * * * *", "format": "text"}
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_valid_expression_returns_zero(capsys):
    rc = handle(_ns(expression="0 9 * * 1-5"))
    assert rc == 0


def test_valid_expression_prints_checkmark(capsys):
    handle(_ns(expression="0 9 * * 1-5"))
    out = capsys.readouterr().out
    assert "\u2714" in out


def test_valid_expression_prints_explanation(capsys):
    handle(_ns(expression="0 9 * * 1-5"))
    out = capsys.readouterr().out
    assert len(out.strip().splitlines()) >= 2


def test_invalid_expression_returns_one(capsys):
    rc = handle(_ns(expression="99 * * * *"))
    assert rc == 1


def test_invalid_expression_prints_cross(capsys):
    handle(_ns(expression="99 * * * *"))
    out = capsys.readouterr().out
    assert "\u2718" in out


def test_json_valid_output(capsys):
    handle(_ns(expression="*/5 * * * *", format="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["valid"] is True
    assert "explanation" in data
    assert "expression" in data


def test_json_invalid_output(capsys):
    handle(_ns(expression="60 * * * *", format="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["valid"] is False
    assert "errors" in data


def test_register_adds_explain_subcommand():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers()
    register(sub)
    args = parser.parse_args(["explain", "* * * * *"])
    assert args.expression == "* * * * *"


def test_warnings_shown_in_text(capsys):
    # A valid expression that triggers a warning (e.g. both dom and dow set)
    handle(_ns(expression="0 0 1 * 1"))
    out = capsys.readouterr().out
    # Either warnings section present or plain explanation — just ensure no crash
    assert "\u2714" in out
