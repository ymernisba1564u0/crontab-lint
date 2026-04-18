"""Tests for crontab_lint.linter."""
import pytest
from crontab_lint.linter import lint_one, lint_many, summary_counts


def test_lint_one_valid():
    result = lint_one("* * * * *")
    assert result.valid is True
    assert result.errors == []


def test_lint_one_invalid():
    result = lint_one("99 * * * *")
    assert result.valid is False
    assert len(result.errors) > 0


def test_lint_one_preserves_expression():
    result = lint_one("0 9 * * 1")
    assert result.expression == "0 9 * * 1"


def test_lint_many_returns_all():
    exprs = ["* * * * *", "0 0 * * *", "bad"]
    results = lint_many(exprs)
    assert len(results) == 3


def test_lint_many_correct_validity():
    exprs = ["* * * * *", "99 * * * *"]
    results = lint_many(exprs)
    assert results[0].valid is True
    assert results[1].valid is False


def test_summary_counts_all_valid():
    results = lint_many(["* * * * *", "0 0 * * *"])
    counts = summary_counts(results)
    assert counts["total"] == 2
    assert counts["valid"] == 2
    assert counts["invalid"] == 0


def test_summary_counts_mixed():
    results = lint_many(["* * * * *", "99 * * * *"])
    counts = summary_counts(results)
    assert counts["valid"] == 1
    assert counts["invalid"] == 1


def test_summary_counts_empty():
    counts = summary_counts([])
    assert counts["total"] == 0
    assert counts["valid"] == 0
