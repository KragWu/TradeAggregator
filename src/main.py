from __future__ import annotations

import os
from datetime import datetime

from dotenv import load_dotenv

from trade_aggregator.boursorama import (
    fetch_boursorama_stock,
    fetch_forum_top_stocks,
    forum_url_to_course_url,
)
from trade_aggregator.formatting import (
    format_name_with_hyperlink,
    format_percentage,
    parse_numeric,
    should_exclude_value,
)
from trade_aggregator.google_sheets import append_rows_to_sheet, get_google_sheet

HEADER = [
    "Date", "Valeur", "ISIN", "Ticker", "Secteur", "Valorisation", "Volume", 
    "Capital échangé", "Cours", "Variation", "Objectif %", "Objectif €", 
    "Objectif Temps", "Probabilité", "Risque", "Support €", "Distance Support", 
    "Résistance €", "Distance Résistance", "Cours atteint", "Tendance", "% atteint", 
    "Différence", "Trompé de sens"
]

def build_data_rows(data_list: list[dict]) -> list[list]:
    """Construit uniquement les lignes de données (sans entête) avec formatting."""
    rows = []
    for data in data_list:
        rows.append([
            datetime.now().isoformat(timespec="seconds"),  # Date
            format_name_with_hyperlink(data.get("name"), data.get("source_url")),  # Valeur
            data.get("isin", ""),
            data.get("ticker", ""),
            data.get("sector", ""),
            parse_numeric(data.get("valuation")),
            parse_numeric(data.get("volume")),
            format_percentage(data.get("capital_exchanged")),
            parse_numeric(data.get("price")),
            format_percentage(data.get("variation")),
        ])
    return rows


def sheet_has_header(sheet) -> bool:
    """Vérifie si la feuille a déjà l'entête."""
    try:
        return sheet.row_values(1) == HEADER
    except Exception:
        return False


def fetch_and_filter_stock(url: str, excluded_values: list[str]) -> dict | None:
    """Centralise la récupération et le filtrage pour éviter la duplication."""
    try:
        data = fetch_boursorama_stock(url)
        # Gestion native si l'API/Scraper renvoie un dictionnaire incomplet ou vide
        if not data or not data.get("name"):
            return None
    except Exception as exc:
        print(f"Erreur lors de la récupération de {url}: {exc}")
        return None

    if should_exclude_value(data.get("name"), excluded_values):
        print(f"  → Exclusion de {data.get('name')} (liste d'exclusion)")
        return None

    return data


def main() -> int:
    load_dotenv()
    
    # 1. Validation immédiate (Fail Fast)
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    if not sheet_id or not credentials_path:
        raise ValueError("GOOGLE_SHEET_ID et GOOGLE_SHEETS_CREDENTIALS doivent être renseignés dans .env")

    worksheet_name = os.getenv("GOOGLE_SHEET_WORKSHEET", "Feuille 1")
    forum_base_url = os.getenv("BOURSORAMA_FORUM_URL", "https://www.boursorama.com/bourse/forum/")
    
    excluded_values = [v.strip() for v in os.getenv("EXCLUDED_VALUES", "").split(",") if v.strip()]
    added_values = [v.strip() for v in os.getenv("ADDED_VALUES", "").split(",") if v.strip()]

    # 2. Récupération des valeurs du Forum
    print(f"Téléchargement de la liste des valeurs depuis le forum ({forum_base_url})...")
    urls = fetch_forum_top_stocks(forum_base_url)
    if not urls:
        raise RuntimeError("Impossible de récupérer la liste des valeurs depuis le forum Boursorama")

    data_list = []
    for url in urls:
        course_url = forum_url_to_course_url(url)
        print(f"Extraction forum -> Cours : {course_url}")
        res = fetch_and_filter_stock(course_url, excluded_values)
        if res:
            data_list.append(res)

    # 3. Récupération des valeurs supplémentaires
    if added_values:
        print(f"\nTraitement des {len(added_values)} valeur(s) supplémentaire(s)...")
        for added_value in added_values:
            if "-" not in added_value:
                print(f"  → Format incorrect pour '{added_value}' (attendu: type-code). Passé.")
                continue
                
            type_value, code_value = added_value.split("-", 1)
            course_url = ""
            
            if type_value == "tracker":
                course_url = f"https://www.boursorama.com/bourse/trackers/cours/{code_value}/"
            elif type_value == "action":
                course_url = f"https://www.boursorama.com/cours/{code_value}/"
            else:
                print(f"  → Type '{type_value}' non supporté pour {code_value}. Passé.")
                continue

            print(f"Récupération additionnelle : {course_url}")
            res = fetch_and_filter_stock(course_url, excluded_values)
            if res:
                data_list.append(res)

    # 4. Export vers Google Sheets
    if not data_list:
        print("Aucune donnée à ajouter (toutes les valeurs ont été exclues ou échecs techniques).")
        return 0

    print("Connexion à Google Sheets...")
    sheet = get_google_sheet(sheet_id, worksheet_name, credentials_path)
    
    if not sheet_has_header(sheet):
        print("Ajout de l'entête...")
        sheet.append_rows([HEADER], value_input_option="RAW")
    
    data_rows = build_data_rows(data_list)
    append_rows_to_sheet(sheet, data_rows)
    print(f"{len(data_rows)} ligne(s) ajoutée(s) à la feuille '{worksheet_name}'.")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
