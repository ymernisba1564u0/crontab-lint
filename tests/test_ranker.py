"""Tests for crontab_lint.ranker."""
import pytest
from crontab_lint.ranker import rank, _frequency_score
from crontab_lint.parser import parse


def test_every_minute_highest_score():
    results = rank(["* * * * *", "0 * * * *", "0 0 * * *"])
    scores = [r.frequency_score for r in results]
    assert scores[0] > scores[1] > scores[2]


def test_every_minute_rank_one():
    results = rank(["0 0 * * *", "* * * * *"])
    by_expr = {r.expression: r for r in results}
    assert by_expr["* * * * *"].rank == 1


def test_invalid_expression_score_is_minus_one():
    results = rank(["not a cron"])
    assert results[0].frequency_score == -1.0
    assert not results[0].valid


def test_invalid_ranked_after_valid():
    results = rank(["not a cron", "* * * * *"])
    by_expr = {r.expression: r for r in results}
    assert by_expr["not a cron"].rank > by_expr["* * * * *"].rank


def test_order_preserved_in_output():
    exprs = ["0 0 * * *", "* * * * *", "0 12 * * 1"]
    results = rank(exprs)
    assert [r.expression for r in results] == exprs


def test_specific_time_lower_than_hourly():
    results = rank(["0 * * * *", "30 6 * * *"])
    by_expr = {r.expression: r for r in results}
    assert by_expr["0 * * * *"].frequency_score > by_expr["30 6 * * *"].frequency_score


def test_step_expression_score():
    pr = parse("*/15 * * * *")
    assert pr is not None
    score = _frequency_score(pr)
    # every 15 min => 96 times/day
    assert abs(score - 96.0) < 1.0


def test_monthly_expression_low_score():
    results = rank(["0 0 1 * *"])
    # roughly 1440 / 31 / 12 ≈ 3.87 ... actually 1440*(1/60)*(1/24)*(1/31)*(1/12)
    assert results[0].frequency_score < 1.0


def test_empty_list():
    assert rank([]) == []


def test_all_invalid():
    results = rank(["bad", "also bad"])
    assert all(not r.valid for r in results)
    assert results[0].rank == 1
    assert results[1].rank == 2
