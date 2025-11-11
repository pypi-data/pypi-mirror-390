# Casabourse

Bibliothèque Python pour accéder aux données de la Bourse de Casablanca (Casablanca Stock Exchange).

Cette petite API fournit des fonctions pour récupérer les cotations en direct, les historiques, les indices,
les volumes et des métriques de marché prêtes à l'emploi. Les exemples d'utilisation se trouvent dans le
répertoire `examples/` (script d'exemple et notebook).

## Installation

Préféré : installer en mode développement depuis le dépôt local :

```powershell
pip install -e .
```

Ou installer les dépendances listées dans `requirements.txt` :

```powershell
pip install -r requirements.txt
```

## Utilisation rapide

Exemples simples (extraits de `examples/example_usage.py` et `examples/debug_live.py`) :

```python
import casabourse as cb

# récupère les données de marché en direct (DataFrame pandas)
df_live = cb.get_live_market_data()
print(df_live.head())

# recherche d'identifiant de symbole à partir d'un ticker
sid = cb.get_symbol_id_from_ticker_auto('AFM')
print('symbol id AFM:', sid)

# historique d'un ticker sur une période
hist = cb.get_historical_data_auto('IAM', '2024-01-01', '2024-12-31')
print(hist.head())

# top gainers / losers
gainers = cb.get_top_gainers(5)
losers = cb.get_top_losers(5)

# exporter les données de marché (ex: CSV)
fname = cb.export_market_data(format='csv')
print('Exporté vers :', fname)
```

Pour des tests plus poussés et du debugging, voir `examples/debug_live.py` qui montre comment inspecter
les fonctions et appeler plusieurs points d'entrée de l'API.

## Contenu principal

Le package expose plusieurs fonctions au niveau racine (importables via `import casabourse as cb`) :

- Gestion du build id et utilitaires : `get_build_id`, `get_build_id_cached`, etc.
- Marché & cotations : `get_live_market_data`, `get_market_data`, `get_top_gainers`, `get_most_active`,
  `get_sector_performance`, `get_market_summary`, `export_market_data`, ...
- Instruments : `get_symbol_id_from_ticker`, `get_historical_data`, `get_technical_indicators`, ...
- Volumes : `get_volume_overview`, `get_volume_data`
- Capitalisation : `get_capitalization_data`, `get_capitalization_overview`
- Indices : `get_all_indices_overview`, `get_index_composition`, `get_index_quotation`, etc.

(Voir `casabourse/__init__.py` pour la liste complète des symboles exportés.)

## Exemples & Notebook

Les exemples disponibles :

- `examples/example_usage.py` : exemples d'appels courants et d'export.
- `examples/debug_live.py` : script d'inspection et debug (niveau logging détaillé possible).
- `examples/example_notebook.ipynb` : notebook Jupyter d'illustration.

### Exemple : tracé historique

Vous pouvez utiliser le script d'exemple `examples/historical_plot.py` pour récupérer l'historique d'un ticker
et tracer le prix de clôture. Le script sauvegarde un PNG dans le répertoire courant.

Exemple d'utilisation (PowerShell) :

```powershell
pip install -e .
pip install pandas matplotlib
python .\examples\historical_plot.py IAM --start 2024-01-01 --end 2024-12-31
```

Le script tente d'identifier automatiquement la colonne « prix de clôture » dans le DataFrame retourné
et tombe sur la première colonne numérique si aucune colonne explicite n'est trouvée.

Si vous préférez un notebook interactif, copiez le code du script dans une cellule et utilisez `%matplotlib inline`.

## Tests

Les tests unitaires simples se trouvent dans `tests/`. Pour lancer la suite de tests :

```powershell
pip install -r requirements.txt
pip install pytest
pytest -q
```

## Licence

Ce projet inclut un fichier `LICENSE` à la racine. Consultez-le pour les conditions d'utilisation.

## Contributions

Les issues et les pull requests sont bienvenues. Pour développer localement, installez en mode editable
(`pip install -e .`) et exécutez les scripts d'exemple ou le notebook.

---

Si vous voulez que j'ajoute des exemples supplémentaires dans le README (par ex. un exemple complet
de récupération historique + graphique), dites-moi lequel et je l'ajoute.

## Documentation (HTML & PDF)

La documentation complète est fournie dans le répertoire `docs/`. Elle est générée avec Sphinx.

Dépendances recommandées pour construire la doc :

```powershell
pip install -r docs/requirements-docs.txt
# pour générer le PDF via LaTeX, installez également une distribution TeX (ex: TeX Live, MiKTeX)
```

Pour construire la documentation (HTML + tentative de PDF) :

```powershell
python .\scripts\build_docs.py
```

Le HTML sera dans `docs/_build/html`. Si `pdflatex` est disponible, un PDF sera généré dans
`docs/_build/latex`.
