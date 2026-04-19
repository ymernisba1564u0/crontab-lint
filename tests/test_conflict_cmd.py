"""Tests for crontab_lint.commands.conflict_cmd."""
import argparse
import json
import pytest
from unittest.mock import patch, MagicMock
from crontab_lint.commands.conflict_cmd import handle, _format_text
from crontab_lint.conflict import ConflictResult


def _ns(**kwargs):
    defaults = dict(expressions=["* * * * *", "0 * * * *"], timezone="UTC", count=10, fmt="text")
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def _result(conflicts=None):
    c = conflicts or []
    return ConflictResult(
        expressions=["* * * * *", "0 * * * *"],
        conflicts=c,
        total_conflicts=len(c),
        checked_occurrences=10,
    )


def test_no_conflicts_returns_zero(capsys):
    with patch("crontab_lint.commands.conflict_cmd.find_conflicts", return_value=_result()):
        code = handle(_ns())
    assert code == 0


def test_conflicts_returns_one(capsys):
    r = _result(conflicts=[("* * * * *", "0 * * * *", "2024-01-01T00:00:00+00:00")])
    with patch("crontab_lint.commands.conflict_cmd.find_conflicts", return_value=r):
        code = handle(_ns())
    assert code == 1


def test_text_no_conflict_shows_checkmark(capsys):
    with patch("crontab_lint.commands.conflict_cmd.find_conflicts", return_value=_result()):
        handle(_ns(fmt="text"))
    out = capsys.readouterr().out
    assert "✔" in out


def test_text_conflict_shows_cross(capsys):
    r = _result(conflicts=[("a", "b", "2024-01-01T00:00:00+00:00")])
    with patch("crontab_lint.commands.conflict_cmd.find_conflicts", return_value=r):
        handle(_ns(fmt="text"))
    out = capsys.readouterr().out
    assert "✖" in out


def test_json_output_is_valid_json(capsys):
    with patch("crontab_lint.commands.conflict_cmd.find_conflicts", return_value=_result()):
        handle(_ns(fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "total_conflicts" in data
    assert "conflicts" in data


def test_single_expression_returns_two(capsys):
    code = handle(_ns(expressions=["* * * * *"]))
    assert code == 2
