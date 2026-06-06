from __future__ import annotations

import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


def fetch_boursorama_page(url: str, timeout: int = 15) -> str:
    """Télécharge le contenu HTML d'une page Boursorama."""
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=timeout)
    response.raise_for_status()
    return response.text


def parse_boursorama_stock(html: str, url: str) -> Dict[str, Optional[str]]:
    """Extrait les informations clés depuis le HTML d'une page Boursorama."""
    soup = BeautifulSoup(html, "html.parser")

    def _extract_text(selector: str) -> Optional[str]:
        element = soup.select_one(selector)
        if element:
            return element.get_text(separator=" ", strip=True)
        return None

    data: Dict[str, Optional[str]] = {
        "source_url": url,
        "name": None,
        "price": None,
        "variation": None,
        "currency": None,
        "description": None,
    }

    title_meta = soup.select_one("meta[property='og:title']")
    if title_meta and title_meta.has_attr("content"):
        data["name"] = title_meta["content"].strip()
    else:
        data["name"] = _extract_text("h1")

    data["price"] = (
        _extract_text("span.c-instrument__last")
        or _extract_text("span.c-instrument__last--value")
        or _extract_text("span.c-instrument__last-value")
    )
    data["variation"] = (
        _extract_text("span.c-instrument__variation")
        or _extract_text("span.c-instrument__variation--percent")
    )
    data["currency"] = _extract_text("span.c-instrument__currency")

    description_meta = soup.select_one("meta[property='og:description']")
    if description_meta and description_meta.has_attr("content"):
        data["description"] = description_meta["content"].strip()

    return data


def fetch_boursorama_stock(url: str) -> Dict[str, Optional[str]]:
    """Récupère et parse les données de Boursorama pour un URL donné."""
    html = fetch_boursorama_page(url)
    return parse_boursorama_stock(html, url)
