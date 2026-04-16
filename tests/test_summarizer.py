"""Tests for crontab_lint.summarizer."""
import pytest
from crontab_lint.summarizer import summarize, SummaryReport

VALID_EXPRS = ["* * * * *", "0 9 * * 1", "30 18 * * 5"]
INVALID_EXPRS = ["99 * * * *", "* * * * 8"]
MIXED = VALID_EXPRS + INVALID_EXPRS


def test_all_valid_counts():
    report = summarize(VALID_EXPRS)
    assert report.total == 3
    assert report.valid == 3
    assert report.invalid == 0


def test_all_invalid_counts():
    report = summarize(INVALID_EXPRS)
    assert report.invalid == 2
    assert report.valid == 0


def test_mixed_counts():
    report = summarize(MIXED)
    assert report.total == 5
    assert report.valid == 3
    assert report.invalid == 2


def test_invalid_expressions_listed():
    report = summarize(MIXED)
    for expr in INVALID_EXPRS:
        assert expr in report.invalid_expressions


def test_valid_pct_all_valid():
    report = summarize(VALID_EXPRS)
    assert report.valid_pct == 100.0


def test_valid_pct_mixed():
    report = summarize(MIXED)
    assert report.valid_pct == 60.0


def test_empty_input():
    report = summarize([])
    assert report.total == 0
    assert report.valid_pct == 0.0


def test_returns_summary_report_instance():
    assert isinstance(summarize(VALID_EXPRS), SummaryReport)
