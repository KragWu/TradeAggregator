from __future__ import annotations

from typing import Iterable
import gspread


def get_google_sheet(sheet_id: str, worksheet_name: str | None, credentials_path: str) -> gspread.Worksheet:
    """Ouvre une feuille Google Sheets spécifique ou par défaut en utilisant un compte de service."""
    client = gspread.service_account(filename=credentials_path)
    spreadsheet = client.open_by_key(sheet_id)
    if worksheet_name:
        return spreadsheet.worksheet(worksheet_name)
    return spreadsheet.sheet1


def append_rows_to_sheet(sheet: gspread.Worksheet, rows: Iterable[list[str]], value_input_option: str = "USER_ENTERED") -> None:
    """Ajoute des lignes de données en fin de feuille de calcul Google Sheets."""
    # Conversion en liste requise par gspread au cas où 'rows' est un générateur
    sheet.append_rows(list(rows), value_input_option=value_input_option)
