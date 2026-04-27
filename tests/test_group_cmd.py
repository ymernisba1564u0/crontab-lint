"""Tests for crontab_lint.commands.group_cmd."""
import argparse
import json
import textwrap
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest

from crontab_lint.commands.group_cmd import handle, _format_text
from crontab_lint.grouper import group


def _write(tmp_path: Path, content: str) -> str:
    f = tmp_path / "exprs.txt"
    f.write_text(textwrap.dedent(content))
    return str(f)


def _ns(file: str, group_by: str = "tag", fmt: str = "text") -> argparse.Namespace:
    return argparse.Namespace(file=file, group_by=group_by, fmt=fmt)


def test_valid_file_returns_zero(tmp_path):
    f = _write(tmp_path, "* * * * *\n0 * * * *\n")
    assert handle(_ns(f)) == 0


def test_missing_file_returns_two(tmp_path):
    assert handle(_ns(str(tmp_path / "missing.txt"))) == 2


def test_text_output_contains_group_by(tmp_path, capsys):
    f = _write(tmp_path, "* * * * *\n")
    handle(_ns(f, group_by="minute"))
    out = capsys.readouterr().out
    assert "minute" in out


def test_text_output_contains_expression(tmp_path, capsys):
    f = _write(tmp_path, "0 0 * * *\n")
    handle(_ns(f))
    out = capsys.readouterr().out
    assert "0 0 * * *" in out


def test_json_output_is_valid_json(tmp_path, capsys):
    f = _write(tmp_path, "* * * * *\n0 * * * *\n")
    handle(_ns(f, fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert "groups" in data


def test_json_output_contains_total(tmp_path, capsys):
    f = _write(tmp_path, "* * * * *\n0 * * * *\n")
    handle(_ns(f, fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 2


def test_json_group_count_present(tmp_path, capsys):
    f = _write(tmp_path, "* * * * *\n")
    handle(_ns(f, fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert "group_count" in data


def test_comments_ignored(tmp_path, capsys):
    f = _write(tmp_path, "# a comment\n* * * * *\n")
    handle(_ns(f, fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 1


def test_format_text_shows_member_count():
    result = group(["* * * * *", "0 * * * *"], group_by="minute")
    text = _format_text(result)
    assert "(" in text and ")" in text
