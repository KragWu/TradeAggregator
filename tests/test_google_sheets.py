from __future__ import annotations

from unittest.mock import MagicMock

import pytest

import gspread

from trade_aggregator.google_sheets import get_google_sheet, append_rows_to_sheet


def test_get_google_sheet_with_worksheet(monkeypatch):
    fake_sheet = MagicMock()
    spreadsheet = MagicMock()
    spreadsheet.worksheet.return_value = fake_sheet

    client = MagicMock()
    client.open_by_key.return_value = spreadsheet

    monkeypatch.setattr(gspread, "service_account", lambda filename=None: client)

    sheet = get_google_sheet("SHEET_ID", "MyTab", "credentials.json")
    assert sheet is fake_sheet
    client.open_by_key.assert_called_once_with("SHEET_ID")


def test_get_google_sheet_default_sheet(monkeypatch):
    spreadsheet = MagicMock()
    spreadsheet.sheet1 = "SHEET1"
    client = MagicMock()
    client.open_by_key.return_value = spreadsheet
    monkeypatch.setattr(gspread, "service_account", lambda filename=None: client)

    sheet = get_google_sheet("SHEET_ID", "", "credentials.json")
    assert sheet == "SHEET1"


def test_append_rows_to_sheet_calls_append():
    sheet = MagicMock()
    rows = [["a", "b"], ["c", "d"]]
    append_rows_to_sheet(sheet, rows, value_input_option="RAW")
    sheet.append_rows.assert_called_once()
    # ensure passed data is a list of rows
    args, kwargs = sheet.append_rows.call_args
    assert isinstance(args[0], list)
