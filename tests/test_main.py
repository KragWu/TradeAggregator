from __future__ import annotations

from trade_aggregator.main import build_rows


def test_build_rows_creates_header_and_row():
    data_list = [
        {
            "source_url": "https://boursorama.test/exm",
            "name": "Exemple",
            "price": "10.0",
            "variation": "+0.5%",
            "currency": "EUR",
            "description": "Desc",
        }
    ]

    rows = build_rows(data_list)
    assert rows[0][0] == "timestamp"
    assert rows[0][1] == "source_url"
    assert len(rows) == 2
    # the second row contains the values in the same order as header
    assert rows[1][1] == "https://boursorama.test/exm"
    assert rows[1][2] == "Exemple"
    assert rows[1][3] == "10.0"
