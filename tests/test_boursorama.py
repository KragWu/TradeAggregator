from __future__ import annotations

from types import SimpleNamespace

import pytest

from trade_aggregator.boursorama import (
    parse_boursorama_stock,
    fetch_boursorama_page,
    fetch_boursorama_stock,
)


SAMPLE_HTML = """
<html>
<head>
  <meta property="og:title" content="Société Exemple (EXM) - Boursorama" />
  <meta property="og:description" content="Cours en temps réel" />
</head>
<body>
  <h1>Société Exemple</h1>
  <div>
    <span class="c-instrument__last">123.45</span>
    <span class="c-instrument__variation">+1.23%</span>
    <span class="c-instrument__currency">EUR</span>
  </div>
</body>
</html>
"""


def test_parse_boursorama_stock_basic():
    data = parse_boursorama_stock(SAMPLE_HTML, url="https://boursorama.test/exm")
    assert data["source_url"] == "https://boursorama.test/exm"
    assert "Société Exemple" in (data["name"] or "")
    assert data["price"] == "123.45"
    assert data["variation"] == "+1.23%"
    assert data["currency"] == "EUR"
    assert data["description"] == "Cours en temps réel"


def test_fetch_boursorama_page_monkeypatched(monkeypatch):
    def fake_get(url, headers=None, timeout=15):
        resp = SimpleNamespace()
        resp.status_code = 200
        resp.text = SAMPLE_HTML

        def raise_for_status():
            return None

        resp.raise_for_status = raise_for_status
        return resp

    monkeypatch.setattr("trade_aggregator.boursorama.requests.get", fake_get)
    html = fetch_boursorama_page("https://boursorama.test/exm")
    assert "Société Exemple" in html


def test_fetch_boursorama_stock_uses_parser(monkeypatch):
    monkeypatch.setattr(
        "trade_aggregator.boursorama.fetch_boursorama_page",
        lambda url: SAMPLE_HTML,
    )
    data = fetch_boursorama_stock("https://boursorama.test/exm")
    assert data["price"] == "123.45"
