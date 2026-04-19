"""Integration-level tests for conflict detection using real scheduler."""
import pytest
from crontab_lint.conflict import find_conflicts


def test_every_minute_vs_every_two_minutes_has_conflicts():
    """*/2 fires on even minutes; * fires every minute — overlap exists."""
    result = find_conflicts(["* * * * *", "*/2 * * * *"], count=10)
    assert result.total_conflicts > 0


def test_every_hour_different_minutes_no_conflict():
    result = find_conflicts(["5 * * * *", "10 * * * *"], count=5)
    assert result.total_conflicts == 0


def test_three_expressions_pairwise_checked():
    """With 3 expressions there are 3 pairs; all identical so all conflict."""
    result = find_conflicts(["0 0 * * *", "0 0 * * *", "0 0 * * *"], count=3)
    # pairs: (0,1), (0,2), (1,2) each share same occurrences
    assert result.total_conflicts >= 3


def test_conflict_times_are_iso_strings():
    result = find_conflicts(["0 6 * * *", "0 6 * * *"], count=2)
    for _, _, ts in result.conflicts:
        assert "T" in ts  # ISO 8601 format


def test_timezone_respected():
    """Should not raise and should return a result for a named timezone."""
    result = find_conflicts(["0 9 * * *", "0 9 * * *"], timezone="America/New_York", count=3)
    assert isinstance(result.total_conflicts, int)
