"""Tests for crontab_lint.aliaser."""
import pytest
from crontab_lint.aliaser import (
    list_aliases,
    resolve_special,
    AliasReport,
    AliasInfo,
    MONTH_ALIASES,
    DOW_ALIASES,
    SPECIAL_ALIASES,
)


# ---------------------------------------------------------------------------
# list_aliases
# ---------------------------------------------------------------------------

def test_list_aliases_returns_alias_report():
    result = list_aliases()
    assert isinstance(result, AliasReport)


def test_month_aliases_count():
    result = list_aliases()
    assert len(result.month_aliases) == len(MONTH_ALIASES)


def test_dow_aliases_count():
    result = list_aliases()
    assert len(result.dow_aliases) == len(DOW_ALIASES)


def test_special_aliases_count():
    result = list_aliases()
    assert len(result.special_aliases) == len(SPECIAL_ALIASES)


def test_total_equals_sum_of_parts():
    result = list_aliases()
    assert result.total == len(MONTH_ALIASES) + len(DOW_ALIASES) + len(SPECIAL_ALIASES)


def test_month_alias_info_fields():
    result = list_aliases()
    jan = next(a for a in result.month_aliases if a.alias == "jan")
    assert isinstance(jan, AliasInfo)
    assert jan.value == 1
    assert jan.field == "month"
    assert "Jan" in jan.description


def test_dow_alias_info_fields():
    result = list_aliases()
    sun = next(a for a in result.dow_aliases if a.alias == "sun")
    assert sun.value == 0
    assert sun.field == "dow"


def test_special_alias_info_contains_expansion():
    result = list_aliases()
    daily = next(a for a in result.special_aliases if a.alias == "@daily")
    assert daily.value == "0 0 * * *"
    assert "0 0 * * *" in daily.description


# ---------------------------------------------------------------------------
# resolve_special
# ---------------------------------------------------------------------------

def test_resolve_yearly():
    assert resolve_special("@yearly") == "0 0 1 1 *"


def test_resolve_annually_same_as_yearly():
    assert resolve_special("@annually") == resolve_special("@yearly")


def test_resolve_daily():
    assert resolve_special("@daily") == "0 0 * * *"


def test_resolve_midnight_same_as_daily():
    assert resolve_special("@midnight") == resolve_special("@daily")


def test_resolve_hourly():
    assert resolve_special("@hourly") == "0 * * * *"


def test_resolve_case_insensitive():
    assert resolve_special("@DAILY") == "0 0 * * *"


def test_resolve_unknown_returns_none():
    assert resolve_special("@unknown") is None


def test_resolve_plain_expression_returns_none():
    assert resolve_special("* * * * *") is None
