"""Additional focused tests for crontab_lint.reporter.build_report."""

from datetime import datetime, timezone

from crontab_lint.reporter import build_report


NOW = datetime(2024, 3, 15, 12, 0, tzinfo=timezone.utc)


def test_report_expression_preserved():
    report = build_report("0 0 * * *", timezone="UTC", count=1, now=NOW)
    assert report.expression == "0 0 * * *"


def test_report_timezone_preserved():
    report = build_report("0 0 * * *", timezone="Europe/London", count=1, now=NOW)
    assert report.timezone == "Europe/London"


def test_report_count_respected():
    report = build_report("* * * * *", timezone="UTC", count=7, now=NOW)
    assert len(report.next_occurrences) == 7


def test_report_occurrences_are_timezone_aware():
    report = build_report("0 8 * * *", timezone="UTC", count=2, now=NOW)
    for dt in report.next_occurrences:
        assert dt.tzinfo is not None


def test_report_errors_empty_for_valid():
    report = build_report("30 6 * * 1-5", timezone="UTC", count=1, now=NOW)
    assert report.errors == []


def test_report_no_occurrences_on_parse_error():
    report = build_report("60 * * * *", timezone="UTC", count=5, now=NOW)
    assert report.next_occurrences == []
    assert not report.is_valid


def test_report_explanation_none_on_parse_error():
    report = build_report("* * * 13 *", timezone="UTC", count=1, now=NOW)
    assert report.explanation is None
