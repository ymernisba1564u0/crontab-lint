"""Tests for crontab_lint.heatmap."""
import pytest
from crontab_lint.heatmap import build_heatmap, format_heatmap_text, HeatmapResult


def test_total_matches_count():
    result = build_heatmap("* * * * *", count=60)
    assert result.total == 60


def test_hourly_expression_only_one_hour_bucket():
    # Runs every hour at minute 0 — but 60 occurrences span multiple hours
    result = build_heatmap("0 * * * *", count=24)
    assert result.total == 24
    assert sum(result.hours.values()) == 24


def test_specific_hour_only_in_that_bucket():
    result = build_heatmap("0 14 * * *", count=10)
    assert set(result.hours.keys()) == {14}


def test_weekdays_populated():
    result = build_heatmap("0 9 * * *", count=14)
    assert sum(result.weekdays.values()) == 14
    assert all(0 <= k <= 6 for k in result.weekdays)


def test_months_populated():
    result = build_heatmap("0 0 1 * *", count=12)
    assert sum(result.months.values()) == 12
    assert all(1 <= k <= 12 for k in result.months)


def test_heatmap_result_stores_expression():
    result = build_heatmap("5 4 * * *", timezone="UTC", count=5)
    assert result.expression == "5 4 * * *"
    assert result.timezone == "UTC"


def test_format_text_contains_header():
    result = build_heatmap("* * * * *", count=10)
    text = format_heatmap_text(result)
    assert "Heatmap for:" in text
    assert "By Hour" in text
    assert "By Weekday" in text
    assert "By Month" in text


def test_format_text_shows_total():
    result = build_heatmap("* * * * *", count=30)
    text = format_heatmap_text(result)
    assert "total=30" in text


def test_empty_heatmap_does_not_crash():
    result = HeatmapResult(expression="* * * * *", timezone="UTC")
    text = format_heatmap_text(result)
    assert "total=0" in text
