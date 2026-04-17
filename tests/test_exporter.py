"""Tests for crontab_lint.exporter."""
import json
import csv
import io

import pytest

from crontab_lint.exporter import export_json, export_csv, _build_rows

VALID_EXPR = "0 9 * * 1-5"
INVALID_EXPR = "99 99 99 99 99"


def test_build_rows_valid_expression():
    rows = _build_rows([VALID_EXPR])
    assert len(rows) == 1
    assert rows[0].valid is True
    assert rows[0].expression == VALID_EXPR
    assert rows[0].explanation != ""


def test_build_rows_invalid_expression():
    rows = _build_rows([INVALID_EXPR])
    assert rows[0].valid is False
    assert len(rows[0].errors) > 0


def test_build_rows_valid_has_next_run():
    rows = _build_rows([VALID_EXPR], timezone="UTC", count=1)
    assert rows[0].next_run != ""


def test_build_rows_invalid_has_empty_next_run():
    rows = _build_rows([INVALID_EXPR])
    assert rows[0].next_run == ""


def test_export_json_returns_valid_json():
    result = export_json([VALID_EXPR])
    data = json.loads(result)
    assert isinstance(data, list)
    assert len(data) == 1


def test_export_json_fields_present():
    data = json.loads(export_json([VALID_EXPR]))
    row = data[0]
    assert "expression" in row
    assert "valid" in row
    assert "explanation" in row
    assert "errors" in row
    assert "next_run" in row


def test_export_json_multiple_expressions():
    data = json.loads(export_json([VALID_EXPR, INVALID_EXPR]))
    assert len(data) == 2
    assert data[0]["valid"] is True
    assert data[1]["valid"] is False


def test_export_csv_returns_string():
    result = export_csv([VALID_EXPR])
    assert isinstance(result, str)


def test_export_csv_has_header():
    result = export_csv([VALID_EXPR])
    reader = csv.reader(io.StringIO(result))
    header = next(reader)
    assert "expression" in header
    assert "valid" in header


def test_export_csv_row_count():
    result = export_csv([VALID_EXPR, INVALID_EXPR])
    reader = csv.reader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) == 3  # header + 2 data rows


def test_export_csv_invalid_errors_joined():
    result = export_csv([INVALID_EXPR])
    reader = csv.reader(io.StringIO(result))
    next(reader)  # skip header
    row = next(reader)
    # errors column should not be empty for invalid
    errors_col = row[3]
    assert errors_col != ""
