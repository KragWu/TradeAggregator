from __future__ import annotations

import requests
import re
from bs4 import BeautifulSoup
from typing import Dict, Optional, List

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/125.0.0.0 Safari/537.36"
)


def fetch_boursorama_page(url: str) -> str:
    """Télécharge le contenu HTML d'une page Boursorama."""
    response = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=15)
    response.raise_for_status()
    return response.text


def parse_boursorama_stock(html: str, url: str) -> dict[str, str | None]:
    """Extrait les informations clés depuis le HTML d'une page Boursorama."""
    soup = BeautifulSoup(html, "html.parser")

    def _extract_text(selector: str) -> str | None:
        element = soup.select_one(selector)
        return element.get_text(separator=" ", strip=True) if element else None

    data: dict[str, str | None] = {
        "source_url": url, "name": None, "price": None, "variation": None,
        "isin": None, "ticker": None, "sector": None, "volume": None,
        "valuation": None, "capital_exchanged": None,
    }

    # 1. Nom de l'action
    name_el = soup.select_one(".c-faceplate__company-link")
    if name_el:
        data["name"] = name_el.get_text(strip=True)
    else:
        title_meta = soup.select_one("meta[property='og:title']")
        if title_meta and title_meta.has_attr("content"):
            data["name"] = title_meta["content"].split("-")[0].replace("Cours", "").strip()

    # 2 & 4. Données boursières via attributs de flux
    data["price"] = _extract_text("[data-ist-last]")
    data["variation"] = _extract_text("[data-ist-variation]")
    data["volume"] = _extract_text("[data-ist-totalvolume]")
    data["capital_exchanged"] = _extract_text("[data-ist-tradecapital]")
    data["valuation"] = _extract_text("[data-ist-valorization]")

    # 3. Code ISIN & Ticker (Sécurisé contre les IndexError et espaces multiples)
    isin_el = soup.select_one(".c-faceplate__isin")
    if isin_el:
        parts = isin_el.get_text(strip=True).split()  # split() vide gère n'importe quel espacement
        if len(parts) >= 1:
            data["isin"] = parts[0]
        if len(parts) >= 2:
            data["ticker"] = parts[1]
        # Gestion des ETF
        if data["ticker"] is None or data["ticker"] == "-":
            match = re.search(r"/1r[TP]([A-Z0-9]+)/", url)
            data["ticker"] = match.group(1) if match else None

    # 5. Secteur d'activité
    for item in soup.select(".c-list-info__item"):
        heading = item.select_one(".c-list-info__heading")
        if heading and "secteur" in heading.get_text(strip=True).lower():
            value_link = item.select_one(".c-list-info__value")
            if value_link:
                data["sector"] = value_link.get_text(strip=True)
                break

    return data

def fetch_boursorama_stock(url: str) -> Dict[str, Optional[str]]:
    """Récupère et parse les données de Boursorama pour un URL donné."""
    html = fetch_boursorama_page(url)
    return parse_boursorama_stock(html, url)


def parse_forum_top_stocks(html: str, base_url: str = "https://www.boursorama.com") -> list[str]:
    """Extrait les URLs des 10 actions les plus lues (Optimisé)."""
    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []
    seen_links: set[str] = set()  # Recherche en O(1)
    
    for a in soup.select("a[href*='/bourse/forum/']"):
        href = a.get("href")
        if not href:
            continue
        if href.startswith("/"):
            href = base_url.rstrip("/") + href
        if not href.startswith("http"):
            continue
            
        normalized = href.rstrip("/")
        if normalized.lower().endswith("/bourse/forum"):
            continue
            
        if normalized not in seen_links:
            seen_links.add(normalized)
            links.append(href)
            
        if len(links) >= 10:
            break
    return links


def forum_url_to_course_url(url: str) -> str:
    """Convertit une URL de forum de valeur Boursorama en URL de page cours."""
    return url.replace("/bourse/forum/", "/cours/")


def fetch_forum_top_stocks(forum_url: str = "https://www.boursorama.com/bourse/forum/", timeout: int = 15) -> List[str]:
    """Télécharge la page forum et renvoie les URLs des 10 actions les plus lues."""
    html = fetch_boursorama_page(forum_url)
    return parse_forum_top_stocks(html)
