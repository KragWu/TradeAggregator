from __future__ import annotations

import argparse
import os
from datetime import datetime
from typing import List

from dotenv import load_dotenv

from trade_aggregator.boursorama import fetch_boursorama_stock
from trade_aggregator.google_sheets import append_rows_to_sheet, get_google_sheet


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Récupère des informations Boursorama et les envoie vers une feuille Google Sheets."
    )
    parser.add_argument(
        "--sheet-id",
        help="ID de la feuille Google Sheets.",
    )
    parser.add_argument(
        "--worksheet-name",
        default=None,
        help="Nom de l'onglet dans la feuille Google Sheets.",
    )
    parser.add_argument(
        "--credentials",
        default=None,
        help="Chemin vers le fichier JSON du compte de service Google.",
    )
    parser.add_argument(
        "--urls",
        nargs="+",
        help="URLs Boursorama à parser. Si absent, la variable BOURSORAMA_URLS est utilisée.",
    )
    return parser.parse_args()


def build_rows(data_list: List[dict]) -> List[List[str]]:
    header = [
        "timestamp",
        "source_url",
        "name",
        "price",
        "variation",
        "currency",
        "description",
    ]
    rows = [header]
    for data in data_list:
        rows.append([
            datetime.utcnow().isoformat(timespec="seconds") + "Z",
            data.get("source_url", ""),
            data.get("name", ""),
            data.get("price", ""),
            data.get("variation", ""),
            data.get("currency", ""),
            data.get("description", ""),
        ])
    return rows


def main() -> int:
    load_dotenv()
    args = parse_args()

    sheet_id = args.sheet_id or os.getenv("GOOGLE_SHEET_ID")
    credentials_path = args.credentials or os.getenv("GOOGLE_SHEETS_CREDENTIALS")
    worksheet_name = args.worksheet_name or os.getenv("GOOGLE_SHEET_WORKSHEET", "Feuille 1")
    urls = args.urls or [url.strip() for url in os.getenv("BOURSORAMA_URLS", "").split(",") if url.strip()]

    if not sheet_id:
        raise ValueError("Le paramètre --sheet-id ou l'option GOOGLE_SHEET_ID doit être renseigné.")
    if not credentials_path:
        raise ValueError(
            "Le paramètre --credentials ou l'option GOOGLE_SHEETS_CREDENTIALS doit être renseigné."
        )
    if not urls:
        raise ValueError(
            "Aucune URL Boursorama fournie. Utilisez --urls ou définissez BOURSORAMA_URLS dans .env."
        )

    data_list = []
    for url in urls:
        print(f"Récupération des données depuis : {url}")
        data = fetch_boursorama_stock(url)
        data_list.append(data)

    rows = build_rows(data_list)
    print("Connexion à Google Sheets...")
    sheet = get_google_sheet(sheet_id, worksheet_name, credentials_path)
    append_rows_to_sheet(sheet, rows)
    print(f"{len(data_list)} ligne(s) ajoutée(s) à la feuille '{worksheet_name}'.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
