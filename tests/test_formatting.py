import pytest
from trade_aggregator.formatting import (
    parse_numeric,
    format_percentage,
    format_name_with_hyperlink,
    should_exclude_value,
)

### 1. Tests pour parse_numeric
@pytest.mark.parametrize("input_value, expected", [
    ("1 234,56", 1234.56),
    ("1.234,56 €", 1234.56),
    ("-4,5%", -4.5),
    ("1,2B", 1200000000.0),
    ("50M EUR", 50000000.0),
    ("10K", 10000.0),
    ("  15.5  ", 15.5),
    # Test anti-faux positifs (lettres présentes mais pas comme multiplicateurs)
    ("10.5 EUR (B)", 10.5), 
    ("100 kr", 100.0),
    ("100 M$", 100000000.0),
    ("100 K€", 100000.0),
    # Cas limites / invalides
    (None, None),
    ("", None),
    ("N/A", None),
    ("--", None),
])
def test_parse_numeric(input_value, expected):
    assert parse_numeric(input_value) == expected


### 2. Tests pour format_percentage
@pytest.mark.parametrize("input_value, expected", [
    ("45%", 0.45),
    ("-0,15%", -0.0015),
    ("0,4567%", 0.004567), # Vérification de la conservation de la précision
    ("Invalide", None),
    (None, None),
])
def test_format_percentage(input_value, expected):
    assert format_percentage(input_value) == expected


### 3. Tests pour format_name_with_hyperlink
def test_format_name_with_hyperlink_nominal():
    name = "TotalEnergies"
    url = "https://www.boursorama.com/cours/TTE"
    expected = '=LIEN_HYPERTEXTE("https://www.boursorama.com/cours/TTE"; "TotalEnergies")'
    assert format_name_with_hyperlink(name, url) == expected


def test_format_name_with_hyperlink_missing_args():
    assert format_name_with_hyperlink(None, "https://url") == ""
    assert format_name_with_hyperlink("Action", None) == "Action"


def test_format_name_with_hyperlink_escaping():
    # Test de protection contre l'injection de guillemets
    name = 'L\'action "Premium"'
    url = "https://url"
    res = format_name_with_hyperlink(name, url)
    assert ' "Premium"' not in res  # Ne doit pas casser la chaîne
    assert '""Premium""' in res     # Format d'échappement valide dans Sheets


### 4. Tests pour should_exclude_value
def test_should_exclude_value_match():
    excluded = ["Air Liquide", "Total"]
    assert should_exclude_value("TOTALENERGIES", excluded) is True
    assert should_exclude_value("Air Liquide SA", excluded) is True


def test_should_exclude_value_no_match():
    excluded = ["Air Liquide", "Total"]
    assert should_exclude_value("BNP Paribas", excluded) is False
    assert should_exclude_value(None, excluded) is False
