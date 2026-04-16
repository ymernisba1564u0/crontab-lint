"""Additional JSON-field tests for summary_cmd."""
import json
import os
import tempfile
import argparse

from crontab_lint.commands.summary_cmd import handle


def _write(lines):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False)
    f.write("\n".join(lines))
    f.close()
    return f.name


def _ns(path, fmt="json"):
    return argparse.Namespace(file=path, format=fmt, func=handle)


def test_json_valid_pct_all_valid(capsys):
    path = _write(["* * * * *", "0 0 * * *"])
    handle(_ns(path))
    data = json.loads(capsys.readouterr().out)
    assert data["valid_pct"] == 100.0
    os.unlink(path)


def test_json_invalid_expressions_listed(capsys):
    path = _write(["99 * * * *"])
    handle(_ns(path))
    data = json.loads(capsys.readouterr().out)
    assert "99 * * * *" in data["invalid_expressions"]
    os.unlink(path)


def test_json_warning_count_present(capsys):
    path = _write(["* * * * *"])
    handle(_ns(path))
    data = json.loads(capsys.readouterr().out)
    assert "warning_count" in data
    os.unlink(path)


def test_empty_file_json(capsys):
    path = _write([])
    handle(_ns(path))
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 0
    os.unlink(path)
