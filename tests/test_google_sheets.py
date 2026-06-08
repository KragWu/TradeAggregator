from unittest.mock import MagicMock, patch
import gspread

from trade_aggregator.google_sheets import get_google_sheet, append_rows_to_sheet


### 1. Tests pour get_google_sheet
@patch("gspread.service_account")
def test_get_google_sheet_with_worksheet_name(mock_service_account):
    # Configuration des mocks en chaîne
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    mock_worksheet = MagicMock()
    
    mock_service_account.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet
    mock_spreadsheet.worksheet.return_value = mock_worksheet

    # Appel de la fonction avec un nom de feuille explicite
    result = get_google_sheet(
        sheet_id="fake_id", 
        worksheet_name="Réflexion PEA", 
        credentials_path="path/to/creds.json"
    )

    # Vérifications
    mock_service_account.assert_called_once_with(filename="path/to/creds.json")
    mock_client.open_by_key.assert_called_once_with("fake_id")
    mock_spreadsheet.worksheet.assert_called_once_with("Réflexion PEA")
    assert result == mock_worksheet


@patch("gspread.service_account")
def test_get_google_sheet_default_sheet1(mock_service_account):
    mock_client = MagicMock()
    mock_spreadsheet = MagicMock()
    # On simule l'attribut .sheet1 de l'objet spreadsheet
    mock_spreadsheet.sheet1 = MagicMock() 
    
    mock_service_account.return_value = mock_client
    mock_client.open_by_key.return_value = mock_spreadsheet

    # Appel avec worksheet_name vide ou None
    result = get_google_sheet(
        sheet_id="fake_id", 
        worksheet_name=None, 
        credentials_path="path/to/creds.json"
    )

    # Vérification que worksheet() n'a PAS été appelé et qu'on a pris sheet1
    mock_spreadsheet.worksheet.assert_not_called()
    assert result == mock_spreadsheet.sheet1


### 2. Tests pour append_rows_to_sheet
def test_append_rows_to_sheet_nominal():
    mock_sheet = MagicMock(spec=gspread.Worksheet)
    data_to_insert = [["2026-06-08", "TotalEnergies", "FR0000120271"]]

    append_rows_to_sheet(mock_sheet, data_to_insert, value_input_option="RAW")

    # On vérifie que la méthode gspread a bien reçu les bons arguments
    mock_sheet.append_rows.assert_called_once_with(
        [["2026-06-08", "TotalEnergies", "FR0000120271"]], 
        value_input_option="RAW"
    )


def test_append_rows_with_generator():
    mock_sheet = MagicMock(spec=gspread.Worksheet)
    
    # On teste le comportement avec un générateur (yield) pour valider le comportement du `list(rows)`
    def rows_generator():
        yield ["Data1", "Data2"]
        yield ["Data3", "Data4"]

    append_rows_to_sheet(mock_sheet, rows_generator())

    # Le mock doit avoir reçu une vraie liste expansée
    mock_sheet.append_rows.assert_called_once_with(
        [["Data1", "Data2"], ["Data3", "Data4"]], 
        value_input_option="USER_ENTERED" # Option par défaut
    )
