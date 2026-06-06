# TradeAggregator

TradeAggregator est un projet Python pour récupérer des informations financières depuis Boursorama et les écrire automatiquement dans une feuille Google Sheets.

## Objectif

- Récupérer des données de pages Boursorama.
- Écrire les informations collectées dans une feuille Google Sheets.
- Automatiser la saisie pour gagner du temps.

## Structure du projet

- `src/main.py` : script principal à lancer.
- `src/trade_aggregator/boursorama.py` : récupération et parsing des pages Boursorama.
- `src/trade_aggregator/google_sheets.py` : interaction avec Google Sheets.
- `requirements.txt` : dépendances Python.
- `.env.example` : exemple de variables d'environnement.

## Installation

1. Créez et activez un environnement virtuel :

```bash
python -m venv .venv
source .venv/Scripts/activate  # sous Windows
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Copiez `.env.example` vers `.env` et mettez à jour les valeurs :

```bash
copy .env.example .env
```

4. Créez une clé de compte de service Google et téléchargez le fichier JSON. Placez-le à la racine du projet ou un autre dossier, puis mettez à jour `GOOGLE_SHEETS_CREDENTIALS`.

5. Partagez la feuille Google avec l'adresse email du compte de service (depuis le fichier JSON).

## Utilisation

1. Éditez `.env` pour renseigner :

- `GOOGLE_SHEETS_CREDENTIALS`
- `GOOGLE_SHEET_ID`
- `GOOGLE_SHEET_WORKSHEET`
- `BOURSORAMA_URLS`

2. Lancez le script :

```bash
python src/main.py
```

3. Vous pouvez aussi passer les paramètres en ligne de commande :

```bash
python src/main.py --sheet-id <ID> --credentials credentials.json --urls https://www.boursorama.com/cours/1rP
```

## Personnalisation

- `--worksheet-name` : nom de l'onglet dans la feuille.
- `--urls` : liste d'URL Boursorama séparées par des espaces.

## Remarques

- Le projet utilise un compte de service Google pour écrire dans une feuille Sheets.
- Ne commitez jamais vos identifiants Google ni votre fichier de compte de service.
