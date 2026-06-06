from __future__ import annotations

from typing import Iterable, List
import gspread

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]


def get_google_sheet(sheet_id: str, worksheet_name: str, credentials_path: str):
    """Ouvre une feuille Google Sheets en utilisant un compte de service."""
    client = gspread.service_account(filename=credentials_path)
    spreadsheet = client.open_by_key(sheet_id)
    if worksheet_name:
        return spreadsheet.worksheet(worksheet_name)
    return spreadsheet.sheet1


def append_rows_to_sheet(sheet, rows: Iterable[List[str]], value_input_option: str = "USER_ENTERED"):
    """Ajoute des lignes en fin de feuille."""
    sheet.append_rows(list(rows), value_input_option=value_input_option)
