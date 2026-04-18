"""Tests for crontab_lint.commands.lint_many_cmd."""
import argparse
import json
import textwrap
from pathlib import Path

import pytest

from crontab_lint.commands.lint_many_cmd import handle


def _write(tmp_path, content: str) -> str:
    p = tmp_path / "exprs.txt"
    p.write_text(textwrap.dedent(content))
    return str(p)


def _ns(file, fmt="text"):
    ns = argparse.Namespace()
    ns.file = file
    ns.format = fmt
    return ns


def test_all_valid_returns_zero(tmp_path):
    f = _write(tmp_path, "* * * * *\n0 9 * * 1\n")
    assert handle(_ns(f)) == 0


def test_has_invalid_returns_one(tmp_path):
    f = _write(tmp_path, "* * * * *\n99 * * * *\n")
    assert handle(_ns(f)) == 1


def test_text_output_contains_checkmark(tmp_path, capsys):
    f = _write(tmp_path, "* * * * *\n")
    handle(_ns(f))
    assert "\u2713" in capsys.readouterr().out


def test_text_output_contains_cross(tmp_path, capsys):
    f = _write(tmp_path, "99 * * * *\n")
    handle(_ns(f))
    assert "\u2717" in capsys.readouterr().out


def test_text_output_contains_totals(tmp_path, capsys):
    f = _write(tmp_path, "* * * * *\n99 * * * *\n")
    handle(_ns(f))
    out = capsys.readouterr().out
    assert "Total: 2" in out
    assert "Invalid: 1" in out


def test_json_output_is_valid_json(tmp_path, capsys):
    f = _write(tmp_path, "* * * * *\n")
    handle(_ns(f, fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert "summary" in data
    assert "results" in data


def test_json_summary_counts(tmp_path, capsys):
    f = _write(tmp_path, "* * * * *\n0 0 * * *\n99 * * * *\n")
    handle(_ns(f, fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["total"] == 3
    assert data["summary"]["valid"] == 2


def test_missing_file_returns_two(tmp_path):
    ns = _ns(str(tmp_path / "missing.txt"))
    assert handle(ns) == 2


def test_comments_ignored(tmp_path, capsys):
    f = _write(tmp_path, "# comment\n* * * * *\n")
    handle(_ns(f, fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["summary"]["total"] == 1
