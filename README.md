# TradeAggregator

TradeAggregator est un projet Python pour récupérer automatiquement les 10 valeurs les plus lues du forum Boursorama, collecter leurs informations financières, et les enregistrer dans une feuille Google Sheets.

## Objectif

- Récupérer les 10 actions les plus lues sur le forum Boursorama.
- Extraire les données financières détaillées (cours, variation, valorisation, volume, etc.) depuis la page de chaque valeur.
- Écrire automatiquement ces informations dans une feuille Google Sheets avec formatage approprié.
- Éviter la saisie manuelle et chronophage dans Google Sheets.

## Fonctionnalités

- **Récupération automatique** : collecte les 10 valeurs les plus actives du forum Boursorama.
- **Extraction de données enrichies** : ISIN, ticker, secteur, valorisation, volume, capital échangé, cours, variation.
- **Formatage intelligent** :
  - Les prix et volumes sont convertis au format numérique.
  - La valorisation est supprimée de la devise (EUR) et convertie en nombre.
  - Le capital échangé est converti en pourcentage (0-1).
  - Les noms des valeurs incluent des hyperliens vers leurs pages Boursorama.
- **Entête conditionnelle** : l'entête n'est écrite qu'une seule fois (pas de doublon).
- **Exclusion paramétrable** : possibilité d'exclure certaines valeurs (ex: CAC 40, EURO STOXX 50).

## Structure du projet

- `src/main.py` : script principal orchestrant la collecte et l'écriture.
- `src/trade_aggregator/boursorama.py` : récupération et parsing des pages Boursorama.
- `src/trade_aggregator/google_sheets.py` : interaction avec Google Sheets.
- `src/trade_aggregator/formatting.py` : formatage des données pour Google Sheets.
- `requirements.txt` : dépendances Python.
- `.env.example` : exemple de variables d'environnement.
- `tests/` : suite de tests unitaires.

## Pré-requis

Pour exécuter ce projet, vous devez installer Python sur votre machine. Voici la procédure selon votre système d'exploitation et votre gestionnaire d'environnement.

### Windows (via vfox)

vfox (Version Fox) est un gestionnaire de versions multi-plateforme simple et moderne.

Ouvrez votre terminal (PowerShell ou Invite de commandes en mode administrateur).

Installez vfox (si ce n'est pas déjà fait) via l'outil Windows winget :
```shell
winget install version-fox.vfox
```
Note : Redémarrez votre terminal après l'installation pour appliquer les changements.

Ajoutez le module Python à vfox :
```shell
vfox add python
```

Installez la version requise (par exemple la version 3.11) :
```shell
vfox install python@3.11
```

Activez-la globalement sur votre session :
```shell
vfox use -g python@3.11
```

### Linux (via SDKMAN!)

SDKMAN! est un outil très populaire pour gérer les versions de vos outils de développement sous Linux.

Ouvrez votre terminal et assurez-vous que SDKMAN est à jour.

Installez Python en exécutant la commande suivante :
```shell
sdk install python 3.11.0-open
```
(Vous pouvez remplacer 3.11.0-open par la version exacte de votre choix).

### macOS (via Homebrew)

Homebrew est le gestionnaire de paquets incontournable sur Mac.

Ouvrez le Terminal (via Spotlight : Cmd + Espace -> taper "Terminal").

Installez Python à l'aide de la commande :
```shell
brew install python@3.11
```

Liez la version pour qu'elle devienne votre version par défaut :
```shell
brew link --overwrite python@3.11
```

### Étape finale : Verification de l'installation

Peu importe votre système d'exploitation, ouvrez un nouveau terminal et tapez la commande suivante pour valider que tout fonctionne :

```shell
python --version
(ou python3 --version sur Mac/Linux)
```

## Installation

1. Créez et activez un environnement virtuel :

```bash
python -m venv .venv
.venv\Scripts\activate
```

2. Installez les dépendances :

```bash
pip install -r requirements.txt
```

3. Copiez `.env.example` vers `.env` :

```bash
copy .env.example .env
```

4. Créez une clé de compte de service Google :
   - Allez sur [Google Cloud Console](https://console.cloud.google.com/) et utilisez votre compte Google.
   - Créez un projet, nommé TradeAggregator
     * Cliquez en haut à gauche `le sélecteur de projets`
     * Cliquez en haut à droite de la popin sur `Nouveau projet`
   - Activez l'API Google Sheets.
     * Cherchez dans la barre de recherche en haut `Google Sheets API`
     * Cliquez sur le bouton `Activer`
   - Activez l'API Google Drive.
     * Cherchez dans la barre de recherche en haut `Google Drive API`
     * Cliquez sur le bouton `Activer`
   - Créez un compte de service.
     * Cliquez dans le menu de navigation en haut à gauche (les 3 barres horizontales)
     * Placez votre curseur de souris sur `IAM et administration`
     * Après ouverture automatique du menu de navigation de cette rubrique, cliquez sur `Comptes de service`
     * Cliquez sur `Créer un compte de service`
     * Nommez le compte de service "scraper" ce qui doit donner l'adresse mail : scraper@trade-aggregator.iam.gserviceaccount.com
     * Appuyer sur le bouton `OK`
   - Créez une clé de compte de service et téléchargez le fichier JSON.
     * Cliquez sur le compte de service `scraper` dans la liste
     * Cliquez sur `Clés` dans le menu en haut (entre `Autorisation` et `Métriques`)
     * Cliquez sur `Ajouter une clé`, puis `Créer une clé`
     * Sélectionnez type de clé `JSON` et appuyez sur le bouton `Créer`
     * Automatique le fichier sera dans votre répertoire `Téléchargements`
   - Placez le fichier JSON à la racine du projet ou un autre chemin, puis mettez à jour `GOOGLE_SHEETS_CREDENTIALS` dans `.env` pour indiquer où se trouve le fichier. (Mettre tous le chemin, exemple : C:/Users/toto/Documents/secret/trade-aggregator-credentials.json)

5. Partagez votre feuille Google Sheets avec l'adresse email du compte de service (visible dans le fichier JSON).
   - Dans votre fichier Google Sheets, cliquez sur le bouton `Partager` en haut à droite
   - Ajoutez l'adresse mail du compte de service précédemment créé avec l'accès `Editeur`.
   - **Décocher** `Envoyer une notification`
   - Cliquez sur le bouton `Partager`

## Configuration (.env)

Remplissez les variables suivantes dans `.env` :

```
# Chemin vers le fichier JSON du compte de service Google
GOOGLE_SHEETS_CREDENTIALS=credentials.json

# ID de la feuille Google Sheets (visible dans l'URL : /d/{ID}/edit)
GOOGLE_SHEET_ID=your_google_sheet_id_here

# Nom de l'onglet (par défaut : "Feuille 1")
GOOGLE_SHEET_WORKSHEET=

# Valeurs à exclure (séparées par des virgules)
# Exemple : CAC 40,EURO STOXX 50,S&P 500
EXCLUDED_VALUES=

# Valeurs supplémentaires à récupérer (séparées par des virgules)
# Exemple : tracker-1rTDCAM,action-1rPTTE
ADDED_VALUES=
```

## Utilisation

Lancez le script :

```bash
python src/main.py
```

### Flux d'exécution

1. Récupère la page du forum Boursorama.
2. Extrait les URLs des 10 valeurs les plus lues.
3. Pour chaque valeur :
   - Récupère la page de la valeur.
   - Parse les données financières.
   - Applique les filtres d'exclusion.
4. Formate les données (valeurs numériques, pourcentages, hyperliens).
5. Vérifie si la feuille Google Sheets a déjà l'entête.
6. Ajoute l'entête si nécessaire.
7. Ajoute les nouvelles lignes de données.

## Format de la feuille Google Sheets

Lorsque la feuille est vide, le script ajoute automatiquement l'en-tête par défaut ci-dessous :

- Date
- Valeur
- ISIN
- Ticker
- Secteur
- Valorisation
- Volume
- Capital échangé
- Cours
- Variation
- Volume Moyen (Google Finance)
- Momentum (Volume / Volume Moy)
- Objectif %
- Objectif €
- Objectif Temps
- Probabilité
- Risque
- Support €
- Distance Support
- Résistance €
- Distance Résistance
- MM20
- Tendance MM20
- MM50
- Tendance MM50
- MM200
- Tendance MM200
- Croisement Doré
- Cours atteint
- % atteint
- Différence
- Trompé de sens
- Code Google Finance

Le script écrit directement les colonnes suivantes : `Date`, `Valeur`, `ISIN`, `Ticker`, `Secteur`, `Valorisation`, `Volume`, `Capital échangé`, `Cours`, `Variation` et `Code Google Finance`.

Si votre feuille Google Sheets contient déjà des colonnes supplémentaires, le script respecte l'ordre des en-têtes existants et ajoute des valeurs vides pour les colonnes qu'il ne gère pas.

## Tests

Lancez les tests unitaires :

```bash
python -m pytest tests/ -v
```

## Remarques de sécurité

- ⚠️ **Ne commitez jamais** vos identifiants Google ni votre fichier de compte de service.
- Le fichier `credentials.json` est inclus dans `.gitignore`.
- Gardez vos variables d'environnement privées.
