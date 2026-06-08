import pytest
from unittest.mock import patch
from main import build_dynamic_row

def test_build_dynamic_row_adaptive_mapping():
    # 1. Données brutes simulées issues du scraper
    mock_data = {
        "name": "TotalEnergies",
        "source_url": "https://url-tte",
        "isin": "FR0000120271",
        "ticker": "TTE",
        "sector": "Énergie"
    }

    # 2. CAS A : L'ordre classique des colonnes
    headers_order_a = ["Date", "Ticker", "ISIN", "Colonne Inconnue Du Sheets"]
    
    with patch("main.format_name_with_hyperlink", return_value="Link"):
        row_a = build_dynamic_row(mock_data, headers_order_a)
        
    assert len(row_a) == 4
    assert row_a[1] == "TTE"          # Ticker est bien en 2ème position (index 1)
    assert row_a[2] == "FR0000120271"   # ISIN en 3ème position
    assert row_a[3] == ""               # La colonne inconnue est laissée vide de manière sécurisée

    # 3. CAS B : L'ordre du fichier Excel a changé en production !
    # Le Ticker est maintenant au début, et une formule personnalisée a été insérée au milieu
    headers_order_b = ["Ticker", "Mon Calcul Manuel", "ISIN", "Date"]
    
    with patch("main.format_name_with_hyperlink", return_value="Link"):
        row_b = build_dynamic_row(mock_data, headers_order_b)
        
    assert len(row_b) == 4
    assert row_b[0] == "TTE"          # Ticker a migré en 1ère position !
    assert row_b[1] == ""               # "Mon Calcul Manuel" est préservé vide pour laisser Sheets calculer
    assert row_b[2] == "FR0000120271"   # ISIN est calé au bon endroit
