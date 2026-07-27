import pytest
import requests
from unittest.mock import patch, MagicMock
from trade_aggregator.boursorama import (
    parse_boursorama_stock, 
    parse_forum_top_stocks, 
    forum_url_to_course_url, 
    fetch_boursorama_page
)

# --- FIXTURES HTML POUR LE PARSING ---
@pytest.fixture
def html_stock_page():
    return """
    <html>
        <meta property="og:title" content="Cours TotalEnergies - ISIN ..." />
        <div class="c-faceplate__company-link">TotalEnergies</div>
        <div class="c-faceplate__isin">FR0000120271   TTE</div>
        <span data-ist-last>62.50</span>
        <span data-ist-variation>+1.20%</span>
        <span data-ist-totalvolume>1 234 567</span>
        <span data-ist-tradecapital>77M€</span>
        <span data-ist-valorization>155B</span>
        <ul>
            <li class="c-list-info__item">
                <span class="c-list-info__heading">Secteur d'activité</span>
                <span class="c-list-info__value">Énergie</span>
            </li>
        </ul>
    </html>
    """

@pytest.fixture
def html_forum_page():
    return """
    <html>
        <a href="/bourse/forum/action-total-FR0000120271-1">Total Thread</a>
        <a href="/bourse/forum/action-total-FR0000120271-1">Doublon à ignorer</a>
        <a href="https://www.boursorama.com/bourse/forum">Lien index à ignorer</a>
        <a href="/bourse/forum/action-axa-FR0000120628-1">Axa Thread</a>
    </html>
    """

# --- TESTS ---

def test_fetch_boursorama_page_success():
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.text = "<html>Faux HTML</html>"
        mock_get.return_value = mock_response
        
        html = fetch_boursorama_page("https://test.com")
        assert html == "<html>Faux HTML</html>"
        mock_response.raise_for_status.assert_called_once()


def test_fetch_boursorama_page_timeout():
    with patch("requests.get", side_effect=requests.exceptions.Timeout):
        with pytest.raises(requests.exceptions.Timeout):
            fetch_boursorama_page("https://test.com")


def test_parse_boursorama_stock_nominal(html_stock_page):
    data = parse_boursorama_stock(html_stock_page, "https://test-url.com")
    
    assert data["source_url"] == "https://test-url.com"
    assert data["name"] == "TotalEnergies"
    assert data["price"] == "62.50"
    assert data["variation"] == "+1.20%"
    assert data["isin"] == "FR0000120271"
    assert data["ticker"] == "TTE"
    assert data["volume"] == "1 234 567"
    assert data["sector"] == "Énergie"


def test_parse_boursorama_stock_fallback_title():
    # Test du fallback og:title quand le sélecteur classique est absent
    html_fallback = """
    <html>
        <meta property="og:title" content="Cours Sanofi - Code ISIN..." />
        <div class="c-faceplate__isin">FR123 SANO</div>
    </html>
    """
    data = parse_boursorama_stock(html_fallback, "https://test-url.com")
    assert data["name"] == "Sanofi"


def test_parse_boursorama_stock_malformed_isin():
    # Cas où le Ticker n'est pas fourni dans la classe ISIN
    html_bad_isin = """
    <html>
        <div class="c-faceplate__isin">FR123_SEUL</div>
    </html>
    """
    data = parse_boursorama_stock(html_bad_isin, "https://test-url.com")
    assert data["isin"] == "FR123_SEUL"
    assert data["ticker"] is None  # Pas de crash grâce au découpage sécurisé

def test_parse_boursorama_stock_malformed_isin_but_code_in_url():
    # Cas où le Ticker n'est pas fourni dans la classe ISIN mais dans l'url
    html_bad_isin = """
    <html>
        <div class="c-faceplate__isin">FR123_SEUL</div>
    </html>
    """
    data = parse_boursorama_stock(html_bad_isin, "https://test-url.com/1rPSEUL/")
    assert data["isin"] == "FR123_SEUL"
    assert data["ticker"] == "SEUL"

    data = parse_boursorama_stock(html_bad_isin, "https://test-url.com/1rTSEUL/")
    assert data["isin"] == "FR123_SEUL"
    assert data["ticker"] == "SEUL"


def test_parse_forum_top_stocks(html_forum_page):
    urls = parse_forum_top_stocks(html_forum_page, base_url="https://www.boursorama.com")
    
    # On attend 2 liens (Total et Axa). Le doublon et l'index forum doivent être éliminés.
    assert len(urls) == 2
    assert urls[0] == "https://www.boursorama.com/bourse/forum/action-total-FR0000120271-1"
    assert urls[1] == "https://www.boursorama.com/bourse/forum/action-axa-FR0000120628-1"


@pytest.mark.parametrize("forum_url, expected_course_url", [
    ("https://www.boursorama.com/bourse/forum/action-total", "https://www.boursorama.com/cours/action-total"),
    ("https://boursorama.com/bourse/forum/", "https://boursorama.com/cours/"),
])
def test_forum_url_to_course_url(forum_url, expected_course_url):
    assert forum_url_to_course_url(forum_url) == expected_course_url
