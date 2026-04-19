import pytest
from crontab_lint.similarity import similarity


def test_identical_expressions_score_one():
    r = similarity("0 9 * * 1", "0 9 * * 1")
    assert r.score == 1.0


def test_identical_matching_fields_five():
    r = similarity("0 9 * * 1", "0 9 * * 1")
    assert r.matching_fields == 5


def test_completely_different_score_zero():
    r = similarity("0 9 1 1 1", "30 18 15 6 5")
    assert r.score == 0.0


def test_wildcard_gives_partial_score():
    # minute matches (both 0), hour differs, rest wildcards match fully
    r = similarity("0 9 * * *", "0 18 * * *")
    # minute=1.0, hour=0.0, day=1.0, month=1.0, dow=1.0 => 4/5=0.8
    assert r.score == 0.8


def test_both_valid_set_for_valid_expressions():
    r = similarity("* * * * *", "0 0 * * *")
    assert r.both_valid is True


def test_invalid_first_expression():
    r = similarity("invalid", "* * * * *")
    assert r.both_valid is False
    assert r.score == 0.0
    assert r.error is not None


def test_invalid_second_expression():
    r = similarity("* * * * *", "bad expr")
    assert r.both_valid is False


def test_expressions_preserved():
    r = similarity("0 9 * * 1", "0 10 * * 1")
    assert r.expression_a == "0 9 * * 1"
    assert r.expression_b == "0 10 * * 1"


def test_total_fields_always_five():
    r = similarity("* * * * *", "* * * * *")
    assert r.total_fields == 5


def test_partial_wildcard_overlap():
    # both wildcards on day/month/dow, same minute, different hour
    r = similarity("5 * * * *", "5 * * * *")
    assert r.matching_fields == 5
    assert r.score == 1.0
