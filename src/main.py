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

# Cet en-tête sert UNIQUEMENT de modèle initial si la feuille Google Sheet est complètement vide.
# Une fois la feuille créée, c'est l'ordre réel du Sheets qui fera foi.
DEFAULT_HEADER = [
    "Date", "Valeur", "ISIN", "Ticker", "Secteur", "Valorisation", "Volume", 
    "Capital échangé", "Cours", "Variation", "Volume Moyen (Google Finance)", 
    "Momentum (Volume / Volume Moy)", "Objectif %", "Objectif €", 
    "Objectif Temps", "Probabilité", "Risque", "Support €", "Distance Support", 
    "Résistance €", "Distance Résistance", "MM20", "Tendance MM20", 
    "MM50", "Tendance MM50", "MM200", "Tendance MM200", "Croisement Doré",
    "Cours atteint", "% atteint", "Différence", "Trompé de sens", "Code Google Finance"
]


def build_dynamic_row(data: dict, sheet_headers: list[str]) -> list:
    """Construit une ligne de données alignée dynamiquement sur l'ordre actuel des colonnes du Sheets."""
    ticker = data.get("ticker", "")
    gf_code = f"EPA:{ticker}" if ticker else ""

    # Association stricte entre le nom exact de la colonne (clé) et la valeur calculée (valeur)
    field_mapping = {
        "Date": datetime.now().isoformat(timespec="seconds"),
        "Valeur": format_name_with_hyperlink(data.get("name"), data.get("source_url")),
        "ISIN": data.get("isin", ""),
        "Ticker": ticker,
        "Secteur": data.get("sector", ""),
        "Valorisation": parse_numeric(data.get("valuation")),
        "Volume": parse_numeric(data.get("volume")),
        "Capital échangé": format_percentage(data.get("capital_exchanged")),
        "Cours": parse_numeric(data.get("price")),
        "Variation": format_percentage(data.get("variation")),
        "Code Google Finance": gf_code,
    }

    # Reconstruction de la ligne en suivant l'ordre exact dicté par les en-têtes du Sheets.
    # Si une colonne du Sheets (ex: une formule ou un objectif) n'est pas gérée par Python,
    # on injecte une chaîne vide "" pour ne pas décaler le reste de la ligne.
    row = []
    for header in sheet_headers:
        row.append(field_mapping.get(header, ""))
        
    return row


def fetch_and_filter_stock(url: str, excluded_values: list[str]) -> dict | None:
    """Centralise la récupération et le filtrage pour éviter la duplication."""
    try:
        data = fetch_boursorama_stock(url)
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
    
    # 1. Validation Fail-Fast
    sheet_id = os.getenv("GOOGLE_SHEET_ID")
    credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    if not sheet_id or not credentials_path:
        raise ValueError("GOOGLE_SHEET_ID et GOOGLE_SHEETS_CREDENTIALS doivent être renseignés dans .env")

    worksheet_name = os.getenv("GOOGLE_SHEET_WORKSHEET", "Feuille 1")
    forum_base_url = "https://www.boursorama.com/bourse/forum/"
    
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

    if not data_list:
        print("Aucune donnée à ajouter (toutes les valeurs ont été exclues ou échecs techniques).")
        return 0

    # 4. Connexion et Alignement Dynamique Google Sheets
    print("Connexion à Google Sheets...")
    sheet = get_google_sheet(sheet_id, worksheet_name, credentials_path)
    
    # Lecture en temps réel de la première ligne du Google Sheet
    try:
        current_headers = sheet.row_values(1)
    except Exception as e:
        print(f"Impossible de lire l'en-tête, tentative de réinitialisation : {e}")
        current_headers = []
    
    # Si le fichier est totalement neuf/vide, on applique l'en-tête par défaut
    if not current_headers:
        print("La feuille est vide. Ajout de l'entête par défaut...")
        sheet.append_rows([DEFAULT_HEADER], value_input_option="RAW")
        current_headers = DEFAULT_HEADER

    print("Génération et alignement des lignes de données...")
    data_rows = [build_dynamic_row(data, current_headers) for data in data_list]
    
    # Envoi groupé en une seule requête API
    append_rows_to_sheet(sheet, data_rows)
    print(f"{len(data_rows)} ligne(s) ajoutée(s) avec succès dans '{worksheet_name}'.")
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
