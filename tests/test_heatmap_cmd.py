"""Tests for crontab_lint.commands.heatmap_cmd."""
import argparse
import json
import pytest
from io import StringIO
from unittest.mock import patch

from crontab_lint.commands.heatmap_cmd import handle


def _ns(**kwargs):
    defaults = {
        "expression": "0 9 * * *",
        "timezone": "UTC",
        "count": 30,
        "format": "text",
    }
    defaults.update(kwargs)
    return argparse.Namespace(**defaults)


def test_valid_expression_returns_zero(capsys):
    assert handle(_ns()) == 0


def test_invalid_expression_returns_one(capsys):
    assert handle(_ns(expression="99 99 99 99 99")) == 1


def test_text_output_contains_heatmap_header(capsys):
    handle(_ns())
    out = capsys.readouterr().out
    assert "Heatmap for:" in out


def test_text_output_contains_by_hour(capsys):
    handle(_ns())
    out = capsys.readouterr().out
    assert "By Hour" in out


def test_json_output_is_valid_json(capsys):
    handle(_ns(format="json"))
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["expression"] == "0 9 * * *"


def test_json_output_contains_totals(capsys):
    handle(_ns(format="json", count=14))
    data = json.loads(capsys.readouterr().out)
    assert data["total"] == 14


def test_json_output_has_hour_buckets(capsys):
    handle(_ns(format="json", count=5))
    data = json.loads(capsys.readouterr().out)
    assert "hours" in data
    assert "9" in data["hours"]


def test_invalid_json_shows_errors(capsys):
    handle(_ns(expression="bad expr", format="json"))
    data = json.loads(capsys.readouterr().out)
    assert data["valid"] is False
    assert len(data["errors"]) > 0
