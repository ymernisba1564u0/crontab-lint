"""Tests for crontab_lint.tags and tag_cmd."""
from __future__ import annotations
import argparse
import json
from io import StringIO
from unittest.mock import patch
import pytest
from crontab_lint.tags import tag, TagResult
from crontab_lint.commands.tag_cmd import handle, _format_text


def _ns(expression: str, fmt: str = "text") -> argparse.Namespace:
    return argparse.Namespace(expression=expression, format=fmt, func=handle)


def test_every_minute_tag():
    r = tag("* * * * *")
    assert r.valid
    assert "every_minute" in r.tags


def test_hourly_tag():
    r = tag("5 * * * *")
    assert r.valid
    assert "hourly" in r.tags
    assert "every_minute" not in r.tags


def test_daily_tag():
    r = tag("0 9 * * *")
    assert r.valid
    assert "daily" in r.tags


def test_weekly_tag():
    r = tag("0 9 * * 1")
    assert r.valid
    assert "weekly" in r.tags


def test_monthly_tag():
    r = tag("0 9 1 * *")
    assert r.valid
    assert "monthly" in r.tags


def test_has_step_tag():
    r = tag("*/15 * * * *")
    assert r.valid
    assert "has_step" in r.tags


def test_has_range_tag():
    r = tag("0 9-17 * * *")
    assert r.valid
    assert "has_range" in r.tags


def test_yearly_tag():
    r = tag("0 0 1 1 *")
    assert r.valid
    assert "yearly" in r.tags


def test_invalid_expression_no_tags():
    r = tag("not a cron")
    assert not r.valid
    assert r.tags == []


def test_tag_result_type():
    r = tag("* * * * *")
    assert isinstance(r, TagResult)


def test_cmd_valid_returns_zero(capsys):
    rc = handle(_ns("0 9 * * *"))
    assert rc == 0


def test_cmd_invalid_returns_one(capsys):
    rc = handle(_ns("bad expr"))
    assert rc == 1


def test_cmd_text_shows_tags(capsys):
    handle(_ns("*/15 * * * *"))
    out = capsys.readouterr().out
    assert "has_step" in out


def test_cmd_json_output(capsys):
    handle(_ns("0 9 * * *", fmt="json"))
    data = json.loads(capsys.readouterr().out)
    assert "tags" in data
    assert isinstance(data["tags"], list)
    assert data["valid"] is True
