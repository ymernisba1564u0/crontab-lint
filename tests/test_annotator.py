import pytest
from crontab_lint.annotator import annotate, AnnotateResult


def test_valid_expression_is_valid():
    r = annotate("0 9 * * 1")
    assert r.valid is True
    assert r.error is None


def test_invalid_expression_not_valid():
    r = annotate("bad expr")
    assert r.valid is False
    assert r.error is not None


def test_fields_count_five_for_valid():
    r = annotate("* * * * *")
    assert len(r.fields) == 5


def test_fields_empty_for_invalid():
    r = annotate("not valid at all")
    assert r.fields == []


def test_field_names():
    r = annotate("0 9 * * 1")
    names = [f.name for f in r.fields]
    assert names == ["minute", "hour", "day-of-month", "month", "day-of-week"]


def test_field_raw_values():
    r = annotate("5 10 1 6 0")
    raws = [f.raw for f in r.fields]
    assert raws == ["5", "10", "1", "6", "0"]


def test_wildcard_description():
    r = annotate("* * * * *")
    assert r.fields[0].description == "every minute"
    assert r.fields[1].description == "every hour"


def test_step_description():
    r = annotate("*/15 * * * *")
    desc = r.fields[0].description
    assert "15" in desc
    assert "every" in desc


def test_range_description():
    r = annotate("0 9-17 * * *")
    desc = r.fields[1].description
    assert "9" in desc and "17" in desc


def test_list_description():
    r = annotate("0 0 1,15 * *")
    desc = r.fields[2].description
    assert "1,15" in desc


def test_annotated_line_contains_short_labels():
    r = annotate("0 9 * * 1")
    line = r.annotated_line()
    assert "min=" in line
    assert "hr=" in line
    assert "dow=" in line


def test_annotated_line_invalid_returns_expression():
    expr = "bad expression here"
    r = annotate(expr)
    assert r.annotated_line() == expr
