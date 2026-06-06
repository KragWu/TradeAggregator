import pytest
from unittest.mock import MagicMock, patch
from main import build_data_rows, fetch_and_filter_stock, sheet_has_header, HEADER


### 1. Tests de la fonction build_data_rows
def test_build_data_rows_mapping():
    # Données simulées renvoyées par le scraper
    mock_data = [{
        "name": "TotalEnergies",
        "source_url": "https://url-total",
        "isin": "FR0000120271",
        "ticker": "TTE",
        "sector": "Énergie",
        "valuation": "150B",
        "volume": "1000000",
        "capital_exchanged": "0.5%",
        "price": "62.5",
        "variation": "1.2%",
    }]
    
    with patch("main.format_name_with_hyperlink", return_value="=LIEN_HYPERTEXTE(...)"):
        rows = build_data_rows(mock_data)
        
    assert len(rows) == 1
    row = rows[0]
    assert len(row) == 10  # On s'assure qu'on remplit bien 10 colonnes sur les 21 du HEADER
    assert row[1] == "=LIEN_HYPERTEXTE(...)"
    assert row[2] == "FR0000120271"
    assert row[3] == "TTE"


### 2. Tests de la fonction sheet_has_header
def test_sheet_has_header_true():
    mock_sheet = MagicMock()
    mock_sheet.row_values.return_value = HEADER
    assert sheet_has_header(mock_sheet) is True


def test_sheet_has_header_false_or_exception():
    mock_sheet = MagicMock()
    mock_sheet.row_values.return_value = ["Date", "Mauvais Entête", "A", "B"]
    assert sheet_has_header(mock_sheet) is False

    # Test si l'API Google Sheets lève une erreur (ex: Token expiré)
    mock_sheet.row_values.side_effect = Exception("API Error")
    assert sheet_has_header(mock_sheet) is False


### 3. Tests de la fonction fetch_and_filter_stock
@patch("main.fetch_boursorama_stock")
def test_fetch_and_filter_stock_success(mock_fetch):
    mock_fetch.return_value = {"name": "Air Liquide", "price": "170"}
    
    with patch("main.should_exclude_value", return_value=False):
        res = fetch_and_filter_stock("https://url-test", excluded_values=[])
        
    assert res == {"name": "Air Liquide", "price": "170"}


@patch("main.fetch_boursorama_stock")
def test_fetch_and_filter_stock_excluded(mock_fetch):
    mock_fetch.return_value = {"name": "Incorporate", "price": "10"}
    
    # Simule le fait que la valeur doit être exclue
    with patch("main.should_exclude_value", return_value=True):
        res = fetch_and_filter_stock("https://url-test", excluded_values=["Incorporate"])
        
    assert res is None


@patch("main.fetch_boursorama_stock")
def test_fetch_and_filter_stock_exception(mock_fetch):
    mock_fetch.side_effect = Exception("HTTP Error 500")
    
    # La fonction doit attraper l'erreur et renvoyer None (pas de crash)
    res = fetch_and_filter_stock("https://url-test", excluded_values=[])
    assert res is None


### 4. Test d'intégration partiel du main (Erreur .env manquante)
def test_main_missing_env_variables():
    from main import main
    with patch("os.getenv", return_value=""):
        with pytest.raises(ValueError, match="GOOGLE_SHEET_ID et GOOGLE_SHEETS_CREDENTIALS doivent être renseignés"):
            main()
