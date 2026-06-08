from __future__ import annotations

import re
from typing import Optional


def parse_numeric(value: Optional[str]) -> Optional[float]:
    """Convertit une chaîne en nombre, en gérant les multiplicateurs financiers (K, M, B)

    et les formats de milliers européens.
    """
    if not value:
        return None

    value_upper = value.upper().strip()

    # 1. Détection stricte des suffixes financiers (doivent être en fin de mot/chaîne)
    # \bK\b ou K(?![A-Z]) s'assure que K n'est pas le début d'un autre mot (ex: KR)
    multi = 1
    if re.search(r'\d\s*B(?![A-Z])', value_upper):
        multi = 1_000_000_000
    elif re.search(r'\d\s*M(?![A-Z])', value_upper):
        multi = 1_000_000
    elif re.search(r'\d\s*K(?![A-Z])', value_upper):
        multi = 1_000

    # 2. Nettoyage des séparateurs de milliers de type "1.234,56"
    # Si la chaîne contient à la fois un point et une virgule, le point est un séparateur de milliers.
    if "." in value_upper and "," in value_upper:
        value_upper = value_upper.replace(".", "")

    # 3. Supprime tout sauf les chiffres, le point, la virgule et le moins
    cleaned = re.sub(r'[^\d.,-]', '', value_upper)
    if not cleaned or cleaned == "-":
        return None

    # 4. Normalisation du séparateur décimal restant
    cleaned = cleaned.replace(',', '.')

    try:
        return float(cleaned) * multi
    except ValueError:
        return None


def format_percentage(value: Optional[str]) -> Optional[float]:
    """Formate une valeur textuelle en pourcentage décimal pour Google Sheets."""
    numeric = parse_numeric(value)
    if numeric is None:
        return None
    # 6 décimales pour préserver jusqu'à 4 chiffres après la virgule en affichage % (ex: 0,1234%)
    return round(numeric / 100, 6)


def format_name_with_hyperlink(name: Optional[str], url: Optional[str]) -> str:
    """Formate le nom avec un hyperlien sécurisé pour Google Sheets (version FR)."""
    if not name or not url:
        return name or ""
    # Sécurisation contre les guillemets internes qui casseraient la formule Excel/Sheets
    safe_name = name.replace('"', '""')
    return f'=LIEN_HYPERTEXTE("{url}"; "{safe_name}")'


def should_exclude_value(name: Optional[str], excluded_names: list[str]) -> bool:
    """Vérifie par correspondance partielle (insensible à la casse) si un nom doit être exclu."""
    if not name:
        return False
    name_lower = name.lower()
    return any(excluded.lower() in name_lower for excluded in excluded_names if excluded.strip())
