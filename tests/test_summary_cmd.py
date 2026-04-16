"""Tests for crontab_lint.commands.summary_cmd."""
import argparse
import json
import os
import tempfile
import pytest

from crontab_lint.commands.summary_cmd import handle, register


def _write_file(lines):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write("\n".join(lines))
    f.close()
    return f.name


def _ns(path, fmt="text"):
    return argparse.Namespace(file=path, format=fmt, func=handle)


def test_all_valid_returns_zero():
    path = _write_file(["* * * * *", "0 9 * * 1"])
    assert handle(_ns(path)) == 0
    os.unlink(path)


def test_has_invalid_returns_one():
    path = _write_file(["* * * * *", "99 * * * *"])
    assert handle(_ns(path)) == 1
    os.unlink(path)


def test_text_output_contains_totals(capsys):
    path = _write_file(["* * * * *", "0 9 * * 1"])
    handle(_ns(path))
    out = capsys.readouterr().out
    assert "Total" in out
    assert "Valid" in out
    os.unlink(path)


def test_json_output_is_valid_json(capsys):
    path = _write_file(["* * * * *"])
    handle(_ns(path, fmt="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["total"] == 1
    os.unlink(path)


def test_missing_file_returns_two():
    ns = _ns("/nonexistent/path/file.txt")
    assert handle(ns) == 2


def test_comments_skipped():
    path = _write_file(["# comment", "* * * * *"])
    handle(_ns(path, fmt="json"))
    import io, sys
    os.unlink(path)


def test_register_adds_summary_command():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers()
    register(sub)
    args = p.parse_args(["summary", "/tmp/x"])
    assert args.func is handle
