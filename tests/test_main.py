import pytest
from datetime import datetime
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

    date_now = datetime.now()
    # 2. CAS A : L'ordre classique des colonnes
    headers_order_a = ["Date", "Ticker", "ISIN", "Volume Moyen (Google Finance)", "MM20", "MM50", "MM200", "Code Google Finance", "Colonne Inconnue Du Sheets"]
    
    with patch("main.format_name_with_hyperlink", return_value="Link"):
        row_a = build_dynamic_row(mock_data, headers_order_a)
    
    assert len(row_a) == 9
    assert row_a[1] == "TTE"          # Ticker est bien en 2ème position (index 1)
    assert row_a[2] == "FR0000120271"   # ISIN en 3ème position
    assert row_a[3] == "=GOOGLEFINANCE(\"EPA:TTE\";\"volumeavg\")"
    assert row_a[4] == f"=MOYENNE(INDEX(GOOGLEFINANCE(\"EPA:TTE\"; \"price\"; DATE({date_now.year};{date_now.month};{date_now.day})-30; DATE({date_now.year};{date_now.month};{date_now.day})); ; 2))"
    assert row_a[5] == f"=MOYENNE(INDEX(GOOGLEFINANCE(\"EPA:TTE\"; \"price\"; DATE({date_now.year};{date_now.month};{date_now.day})-80; DATE({date_now.year};{date_now.month};{date_now.day})); ; 2))"
    assert row_a[6] == f"=MOYENNE(INDEX(GOOGLEFINANCE(\"EPA:TTE\"; \"price\"; DATE({date_now.year};{date_now.month};{date_now.day})-290; DATE({date_now.year};{date_now.month};{date_now.day})); ; 2))"
    assert row_a[7] == "EPA:TTE"
    assert row_a[8] == ""               # La colonne inconnue est laissée vide de manière sécurisée

    # 3. CAS B : L'ordre du fichier Excel a changé en production !
    # Le Ticker est maintenant au début, et une formule personnalisée a été insérée au milieu
    headers_order_b = ["Ticker", "Mon Calcul Manuel", "ISIN", "Date", "", "Code Google Finance"]
    
    with patch("main.format_name_with_hyperlink", return_value="Link"):
        row_b = build_dynamic_row(mock_data, headers_order_b)
        
    assert len(row_b) == 6
    assert row_b[0] == "TTE"          # Ticker a migré en 1ère position !
    assert row_b[1] == ""               # "Mon Calcul Manuel" est préservé vide pour laisser Sheets calculer
    assert row_b[2] == "FR0000120271"   # ISIN est calé au bon endroit
    assert row_b[5] == "EPA:TTE"
