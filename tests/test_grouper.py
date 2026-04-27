"""Tests for crontab_lint.grouper."""
import pytest
from crontab_lint.grouper import group, GroupResult


DEFAULT_EXPRS = [
    "* * * * *",
    "0 * * * *",
    "0 0 * * *",
    "0 0 * * 0",
    "*/5 * * * *",
]


def test_returns_group_result():
    result = group(DEFAULT_EXPRS)
    assert isinstance(result, GroupResult)


def test_total_matches_input_length():
    result = group(DEFAULT_EXPRS)
    assert result.total == len(DEFAULT_EXPRS)


def test_expressions_preserved():
    result = group(DEFAULT_EXPRS)
    assert result.expressions == DEFAULT_EXPRS


def test_group_by_stored():
    result = group(DEFAULT_EXPRS, group_by="hour")
    assert result.group_by == "hour"


def test_group_by_tag_default():
    result = group(DEFAULT_EXPRS)
    assert result.group_by == "tag"


def test_group_count_positive():
    result = group(DEFAULT_EXPRS)
    assert result.group_count >= 1


def test_all_expressions_in_some_group():
    result = group(DEFAULT_EXPRS)
    all_grouped = [e for exprs in result.groups.values() for e in exprs]
    assert sorted(all_grouped) == sorted(DEFAULT_EXPRS)


def test_invalid_expression_goes_to_invalid_group():
    result = group(["not a cron"])
    assert "__invalid__" in result.groups
    assert "not a cron" in result.groups["__invalid__"]


def test_group_by_minute_same_minute():
    exprs = ["0 1 * * *", "0 2 * * *", "0 3 * * *"]
    result = group(exprs, group_by="minute")
    assert "0" in result.groups
    assert len(result.groups["0"]) == 3


def test_group_by_hour_buckets():
    exprs = ["0 6 * * *", "30 6 * * *", "0 12 * * *"]
    result = group(exprs, group_by="hour")
    assert "6" in result.groups
    assert "12" in result.groups
    assert len(result.groups["6"]) == 2


def test_group_count_equals_keys():
    result = group(DEFAULT_EXPRS, group_by="minute")
    assert result.group_count == len(result.groups)


def test_unknown_group_by_raises():
    with pytest.raises(ValueError, match="Unknown group_by"):
        group(DEFAULT_EXPRS, group_by="second")


def test_empty_input_returns_empty_groups():
    result = group([])
    assert result.total == 0
    assert result.groups == {}
    assert result.group_count == 0
