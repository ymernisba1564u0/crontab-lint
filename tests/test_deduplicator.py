"""Tests for crontab_lint.deduplicator."""
import pytest

from crontab_lint.deduplicator import DeduplicateResult, deduplicate


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

EVERY_MINUTE = "* * * * *"
DAILY_NOON = "0 12 * * *"
DAILY_NOON_ALT = "0 12 * * *"  # identical string
MONTH_ALIAS = "0 0 1 JAN *"
MONTH_NUMERIC = "0 0 1 1 *"  # same after normalisation


# ---------------------------------------------------------------------------
# Basic structure
# ---------------------------------------------------------------------------

def test_returns_deduplicate_result():
    result = deduplicate([EVERY_MINUTE])
    assert isinstance(result, DeduplicateResult)


def test_original_preserved():
    exprs = [EVERY_MINUTE, DAILY_NOON]
    result = deduplicate(exprs)
    assert result.original == exprs


# ---------------------------------------------------------------------------
# No duplicates
# ---------------------------------------------------------------------------

def test_no_duplicates_unique_equals_input():
    exprs = [EVERY_MINUTE, DAILY_NOON]
    result = deduplicate(exprs)
    assert result.unique == exprs


def test_no_duplicates_count_zero():
    result = deduplicate([EVERY_MINUTE, DAILY_NOON])
    assert result.duplicate_count == 0


def test_no_duplicates_unique_count():
    result = deduplicate([EVERY_MINUTE, DAILY_NOON])
    assert result.unique_count == 2


# ---------------------------------------------------------------------------
# Exact duplicates
# ---------------------------------------------------------------------------

def test_exact_duplicate_detected():
    result = deduplicate([DAILY_NOON, DAILY_NOON_ALT])
    assert result.duplicate_count == 1


def test_exact_duplicate_unique_has_one():
    result = deduplicate([DAILY_NOON, DAILY_NOON_ALT])
    assert result.unique_count == 1
    assert result.unique == [DAILY_NOON]


def test_exact_duplicate_tuple_structure():
    result = deduplicate([DAILY_NOON, DAILY_NOON_ALT])
    dup_expr, canonical = result.duplicates[0]
    assert dup_expr == DAILY_NOON_ALT
    assert canonical == DAILY_NOON


# ---------------------------------------------------------------------------
# Alias-equivalent duplicates
# ---------------------------------------------------------------------------

def test_alias_and_numeric_are_duplicates():
    result = deduplicate([MONTH_NUMERIC, MONTH_ALIAS])
    assert result.duplicate_count == 1


def test_alias_duplicate_first_occurrence_kept():
    result = deduplicate([MONTH_NUMERIC, MONTH_ALIAS])
    assert result.unique == [MONTH_NUMERIC]


# ---------------------------------------------------------------------------
# Multiple duplicates
# ---------------------------------------------------------------------------

def test_multiple_duplicates_counted():
    exprs = [EVERY_MINUTE, DAILY_NOON, EVERY_MINUTE, EVERY_MINUTE]
    result = deduplicate(exprs)
    assert result.duplicate_count == 2


def test_empty_list_returns_empty_result():
    result = deduplicate([])
    assert result.unique == []
    assert result.duplicate_count == 0
    assert result.unique_count == 0
