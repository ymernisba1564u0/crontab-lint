"""Tests for crontab_lint.segmenter."""
import pytest

from crontab_lint.segmenter import segment, SegmentResult


def test_returns_segment_result():
    result = segment("* * * * *")
    assert isinstance(result, SegmentResult)


def test_valid_expression_is_valid():
    result = segment("0 9 * * 1")
    assert result.valid is True


def test_invalid_expression_is_not_valid():
    result = segment("99 * * * *")
    assert result.valid is False


def test_invalid_expression_has_errors():
    result = segment("99 * * * *")
    assert len(result.errors) > 0


def test_invalid_expression_has_empty_segments():
    result = segment("99 * * * *")
    assert result.segments == []


def test_five_segments_for_valid():
    result = segment("* * * * *")
    assert len(result.segments) == 5


def test_field_names_in_order():
    result = segment("* * * * *")
    names = [s["field"] for s in result.segments]
    assert names == ["minute", "hour", "day_of_month", "month", "day_of_week"]


def test_wildcard_type():
    result = segment("* * * * *")
    for seg in result.segments:
        assert seg["type"] == "wildcard"


def test_literal_type():
    result = segment("0 9 1 1 1")
    for seg in result.segments:
        assert seg["type"] == "literal"


def test_step_type_detected():
    result = segment("*/5 * * * *")
    assert result.segments[0]["type"] == "step"


def test_range_type_detected():
    result = segment("0 9-17 * * *")
    assert result.segments[1]["type"] == "range"


def test_list_type_detected():
    result = segment("0 9 * * 1,3,5")
    assert result.segments[4]["type"] == "list"


def test_minute_range_bounds():
    result = segment("* * * * *")
    minute_seg = result.segments[0]
    assert minute_seg["range"] == {"min": 0, "max": 59}


def test_hour_range_bounds():
    result = segment("* * * * *")
    hour_seg = result.segments[1]
    assert hour_seg["range"] == {"min": 0, "max": 23}


def test_expression_preserved():
    expr = "30 6 * * *"
    result = segment(expr)
    assert result.expression == expr


def test_raw_value_matches_input():
    result = segment("30 6 * * *")
    raws = [s["raw"] for s in result.segments]
    assert raws == ["30", "6", "*", "*", "*"]
