"""Integration tests for the grouper module using realistic expressions."""
from crontab_lint.grouper import group


HOURLY = "0 * * * *"
DAILY_MIDNIGHT = "0 0 * * *"
DAILY_NOON = "0 12 * * *"
WEEKLY = "0 0 * * 0"
EVERY_MINUTE = "* * * * *"
EVERY_5 = "*/5 * * * *"


def test_every_minute_grouped_alone_by_tag():
    result = group([EVERY_MINUTE, HOURLY, DAILY_MIDNIGHT])
    # every-minute should get its own tag group
    all_keys = list(result.groups.keys())
    assert len(all_keys) >= 2


def test_daily_expressions_share_hour_group():
    result = group([DAILY_MIDNIGHT, DAILY_NOON], group_by="dom")
    # both have dom="*"
    assert "*" in result.groups
    assert len(result.groups["*"]) == 2


def test_weekly_dow_group():
    result = group([WEEKLY, DAILY_MIDNIGHT], group_by="dow")
    assert "0" in result.groups
    assert "*" in result.groups


def test_mixed_valid_invalid():
    result = group([EVERY_MINUTE, "bad expression"])
    assert "__invalid__" in result.groups
    assert result.total == 2


def test_group_by_month_wildcard_all_together():
    exprs = [EVERY_MINUTE, HOURLY, DAILY_MIDNIGHT, WEEKLY, EVERY_5]
    result = group(exprs, group_by="month")
    # all have month="*"
    assert result.group_count == 1
    assert "*" in result.groups
    assert len(result.groups["*"]) == 5
