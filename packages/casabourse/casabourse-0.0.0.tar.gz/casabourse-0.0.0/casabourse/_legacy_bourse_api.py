import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime, timedelta
from typing import List, Union, Optional
import json
import warnings
from urllib3.exceptions import InsecureRequestWarning
import logging

# Supprimer les warnings FutureWarning
warnings.simplefilter(action='ignore', category=FutureWarning)
warnings.filterwarnings('ignore')
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Import des utilitaires depuis le module central
# Si possible importer get_build_id_cached ou mettre la fonction dans le même fichier
# from your_module import get_build_id_cached  # Adapter l'import
# NB : Si toutes les fonctions sont dans le même fichier, appeler directement get_build_id_cached() sans import
# Import des utilitaires depuis le module central
from .utils import (
    get_build_id_cached, 
    format_number_french, 
    with_build_id,
    get_build_id,
    format_mad
)

logger = logging.getLogger(__name__)


def get_instrument_details_(url_instrument):
    """Récupère les données détaillées d'un instrument depuis les deux URLs"""
    try:
        # Première requête: données de l'instrument (avec /symbol)
        response1 = requests.get(url_instrument, verify=False, timeout=10)
        instrument_data = {}

        if response1.status_code == 200:
            data = response1.json()
            attributes = data['data']['attributes']

            instrument_data = {
                'Symbole_id': attributes.get('drupal_internal__id'),
                'Symbole': attributes.get('symbol'),
                'Libellé AR': attributes.get('libelleAR'),
                'Libellé EN': attributes.get('libelleEN'),
                'Libellé FR': attributes.get('libelleFR'),
                'Nombre de titres': attributes.get('nombreTitres'),
                'Code ISIN': attributes.get('codeISIN'),
                'Date introduction': attributes.get('dateIntroduction'),
                'Valeur nominale': attributes.get('valeurNominale'),
                'Code instrument bourse': attributes.get('codeInstrumentBourse'),
                'Cours introduction': attributes.get('coursIntroduction'),
                'Mode cotation': attributes.get('modeCotation'),
                'Non liquide': attributes.get('nonLiquide'),
                'Radie': attributes.get('radie')
            }

        # Deuxième requête: données market_watch (sans /symbol)
        url_market_watch = url_instrument.replace('/symbol', '')
        response2 = requests.get(url_market_watch, verify=False, timeout=10)
        market_data = {}

        if response2.status_code == 200:
            data = response2.json()
            attributes = data['data']['attributes']

            # Traitement des dernières transactions
            last_transactions = attributes.get('lastTransactions', [])
            transactions_count = len(last_transactions)

            # Calculer le volume des dernières transactions
            last_transactions_volume = sum(
                float(tx.get('executedSize', 0)) * float(tx.get('executedPrice', 0))
                for tx in last_transactions if tx.get('executedSize') and tx.get('executedPrice')
            )

            # Dernière transaction (si disponible)
            last_tx = last_transactions[0] if last_transactions else {}

            market_data = {
                'Code market watch': attributes.get('code'),
                'Prix de clôture': attributes.get('closingPrice'),
                'Cours ajusté': attributes.get('coursAjuste'),
                'Cours clôture précédent': attributes.get('coursCloture'),
                'Différence absolue': attributes.get('difference'),
                'Prix de référence dynamique': attributes.get('dynamicReferencePrice'),
                'Variation annuelle': attributes.get('instrumentVarYear'),
                'Dernier prix échangé': attributes.get('lastTradedPrice'),
                'Heure dernière transaction': attributes.get('lastTradedTime'),
                'Prix théorique ouverture': attributes.get('pto'),
                'Ratio ajustement': attributes.get('ratioAjustement'),
                'Ratio consolidé': attributes.get('ratioConsolide'),
                'Heure transaction': attributes.get('transactTime'),
                'Variation PTO': attributes.get('varPTO'),

                # Données sur les dernières transactions
                'Nombre dernières transactions': transactions_count,
                'Volume dernières transactions': last_transactions_volume,
                'Dernière transaction prix': last_tx.get('executedPrice'),
                'Dernière transaction quantité': last_tx.get('executedSize'),
                'Dernière transaction heure': last_tx.get('transactTime'),

                # Stocker les transactions complètes en JSON pour analyse ultérieure
                'Transactions JSON': json.dumps(last_transactions) if last_transactions else None
            }

        # Fusionner les données des deux sources
        return {**instrument_data, **market_data}

    except Exception as e:
        print(f"Erreur lors de la récupération des données pour {url_instrument}: {str(e)}")
        return {}


@with_build_id
def get_live_market_data(build_id=None, formatted=True):
    """
    Récupère les données complètes du marché actions avec buildId dynamique
    
    Args:
        build_id (str): BuildId dynamique (si None, sera récupéré automatiquement)
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        pd.DataFrame: DataFrame avec toutes les données du marché
    """
    
    # Récupérer le buildId si non fourni
    if build_id is None:
        # from your_module import get_build_id_cached  # Adapter l'import selon votre structure
        build_id = get_build_id_cached()
        if not build_id:
            print("❌ Impossible de récupérer le buildId")
            return None
    
    print(f"🔧 Utilisation du buildId: {build_id}")
    
    # URL principale avec buildId dynamique
    url = f'https://www.casablanca-bourse.com/_next/data/{build_id}/fr/live-market/marche-actions-listing.json'
    
    # Headers pour la requête
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    
    try:
        print("📊 Récupération des données du marché actions...")
        response = requests.get(url, headers=headers, verify=False, timeout=30)

        if response.status_code != 200:
            print(f"❌ Erreur {response.status_code} lors de la récupération des données principales")
            return None

        data = response.json()
        paragraphs = data['pageProps']['node']['field_vactory_paragraphs']

        for block in paragraphs:
            widget_id = block.get('field_vactory_component', {}).get('widget_id', '')
            if widget_id == 'bourse_data_listing:marches-actions':
                raw_json = block['field_vactory_component']['widget_data']
                parsed_json = json.loads(raw_json)

                # 📦 Accès aux données de marché
                instruments_data = parsed_json['extra_field']['collection']['data']['data']

                # 📦 Accès aux labels des instruments
                instrument_labels = parsed_json.get('instruments', [])
                uuid_to_label = {inst['uuid']: inst['label'] for inst in instrument_labels}

                # 🧮 Construction du DataFrame
                rows = []
                total_instruments = len(instruments_data)
                print(f"🔄 Récupération des données pour {total_instruments} instruments...")

                for i, item in enumerate(instruments_data):
                    attr = item['attributes']
                    symbol_data = item['relationships']['symbol']['data']
                    symbol_uuid = symbol_data['id']
                    label = uuid_to_label.get(symbol_uuid, symbol_uuid)
                    url_instrument = item['relationships']['symbol']['links']['related']['href']

                    # Formatage des nombres si demandé
                    def format_if_needed(value):
                        if formatted and value is not None:
                            try:
                                return format_number_french(float(value))
                            except (ValueError, TypeError):
                                return value
                        return value

                    # Données de base du marché
                    row_data = {
                        'Instrument': label,
                        'URL': url_instrument,
                        'Statut': attr.get('etatCotVal'),
                        'Cours de référence': format_if_needed(attr.get('staticReferencePrice')),
                        'Ouverture': format_if_needed(attr.get('openingPrice')),
                        'Dernier cours': format_if_needed(attr.get('coursCourant')),
                        'Quantité échangée': format_if_needed(attr.get('cumulTitresEchanges')),
                        'Volume': format_if_needed(attr.get('cumulVolumeEchange')),
                        'Variation en %': attr.get('varVeille'),
                        '+ haut jour': format_if_needed(attr.get('highPrice')),
                        '+ bas jour': format_if_needed(attr.get('lowPrice')),
                        'Meilleur prix à l\'achat': format_if_needed(attr.get('bestBidPrice')),
                        'Quantité Meilleur prix à l\'achat': format_if_needed(attr.get('bestBidSize')),
                        'Meilleur prix à la vente': format_if_needed(attr.get('bestAskPrice')),
                        'Quantité Meilleur prix à la vente': format_if_needed(attr.get('bestAskSize')),
                        'Capitalisation': format_if_needed(attr.get('capitalisation')),
                        'Nombre de transaction': attr.get('totalTrades')
                    }

                    # Récupération des données détaillées (instrument + market_watch)
                    print(f"  📈 Récupération des données détaillées pour {label} ({i+1}/{total_instruments})")
                    details = get_instrument_details_(url_instrument)
                    
                    # Formater les nombres dans les détails si demandé
                    if formatted:
                        numeric_fields = [
                            'Prix de clôture', 'Cours ajusté', 'Cours clôture précédent',
                            'Différence absolue', 'Prix de référence dynamique', 
                            'Dernier prix échangé', 'Prix théorique ouverture',
                            'Volume dernières transactions', 'Dernière transaction prix',
                            'Dernière transaction quantité'
                        ]
                        for field in numeric_fields:
                            if field in details and details[field]:
                                try:
                                    details[field] = format_number_french(float(details[field]))
                                except (ValueError, TypeError):
                                    pass

                    # Fusion des données détaillées avec les données de base
                    row_data.update(details)

                    # Pause pour éviter de surcharger le serveur
                    time.sleep(0.2)

                    rows.append(row_data)

                # Création du DataFrame
                df = pd.DataFrame(rows)
                print(f"✅ Données du marché récupérées avec succès: {len(df)} instruments")
                return df

        print("❌ Widget 'bourse_data_listing:marches-actions' non trouvé")
        return None
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données du marché: {e}")
        return None

# def format_number_french(number):
#     """
#     Formate un nombre avec des espaces pour les milliers et une virgule pour les décimales
#     Format français : 48 364 865,45
#     """
#     if pd.isna(number) or number == 0:
#         return "0"
    
#     try:
#         # Convertir en float puis en int pour la partie entière
#         number_float = float(number)
#         integer_part = int(number_float)
#         decimal_part = round(number_float - integer_part, 2)
        
#         # Formater la partie entière avec des espaces
#         formatted_integer = f"{integer_part:,}".replace(",", " ")
        
#         # Ajouter la partie décimale si nécessaire
#         if decimal_part > 0:
#             decimal_str = f"{decimal_part:.2f}".split('.')[1]
#             return f"{formatted_integer},{decimal_str}"
#         else:
#             return formatted_integer
#     except (ValueError, TypeError):
#         return str(number)


# def format_number_french(number):
#     """
#     Formate un nombre avec des espaces pour les milliers et une virgule pour les décimales
#     Format français : 48 364 865,45
#     """
#     if pd.isna(number) or number == 0:
#         return "0"
    
#     # Séparer partie entière et décimale
#     integer_part = int(number)
#     decimal_part = round(number - integer_part, 2)
    
#     # Formater la partie entière avec des espaces
#     formatted_integer = f"{integer_part:,}".replace(",", " ")
    
#     # Ajouter la partie décimale si nécessaire
#     if decimal_part > 0:
#         decimal_str = f"{decimal_part:.2f}".split('.')[1]
#         return f"{formatted_integer},{decimal_str}"
#     else:
#         return formatted_integer

@with_build_id
def get_live_market_data_auto(build_id=None, formatted=True):
    """
    Version avec injection automatique du buildId
    """
    return get_live_market_data(build_id=build_id, formatted=formatted)

# # Exemple d'utilisation
# if __name__ == "__main__":
#     # Méthode 1: Récupération automatique du buildId
#     print("=== MÉTHODE 1: Récupération automatique ===")
#     df_market = get_live_market_data_auto(formatted=True)
    
#     if df_market is not None:
#         # Sauvegarde en CSV
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"marche_actions_casablanca_complet_avec_details_{timestamp}.csv"
#         df_market.to_csv(filename, index=False, encoding='utf-8-sig')

#         print("✅ Données sauvegardées avec succès!")
#         print(f"📊 Fichier: {filename}")
#         print(f"📊 Shape du DataFrame: {df_market.shape}")
#         print(f"📊 Colonnes disponibles: {len(df_market.columns)}")
#         print("\nAperçu des données:")
#         print(df_market.head()[['Instrument', 'Symbole', 'Dernier cours', 'Variation en %', 'Nombre dernières transactions']])

#         # Afficher les statistiques des transactions
#         tx_counts = df_market['Nombre dernières transactions'].fillna(0)
#         print(f"\n📈 Statistiques des transactions:")
#         print(f"   - Instruments avec transactions: {(tx_counts > 0).sum()}/{len(df_market)}")
#         print(f"   - Nombre moyen de transactions: {tx_counts.mean():.1f}")
#         print(f"   - Maximum de transactions: {tx_counts.max()}")

    # # Méthode 2: Récupération manuelle du buildId
    # print("\n=== MÉTHODE 2: Récupération manuelle ===")
    # # from your_module import get_build_id_cached  # Adapter l'import
    # build_id = get_build_id_cached()
    
    # if build_id:
    #     df_market_manual = get_live_market_data(build_id=build_id, formatted=True)
    #     if df_market_manual is not None:
    #         print(f"✅ Données récupérées avec buildId manuel: {len(df_market_manual)} instruments")


# Nouvelle version des Fonctions
# get_historical_data et get_symbol_id_from_ticker
# get_multiple_symbol_ids

@with_build_id
def get_symbol_id_from_ticker(ticker, build_id=None):
    """
    Récupère le Symbole_id (drupal_internal__id) à partir du ticker avec buildId dynamique
    """
    print(f"🔧 Recherche du ticker '{ticker}' avec buildId: {build_id}")
    
    # URL principale avec buildId dynamique
    url = f'https://www.casablanca-bourse.com/_next/data/{build_id}/fr/live-market/marche-actions-listing.json'

    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }
        
        response = requests.get(url, headers=headers, verify=False, timeout=30)
        if response.status_code == 200:
            data = response.json()
            paragraphs = data['pageProps']['node']['field_vactory_paragraphs']

            for block in paragraphs:
                widget_id = block.get('field_vactory_component', {}).get('widget_id', '')
                if widget_id == 'bourse_data_listing:marches-actions':
                    raw_json = block['field_vactory_component']['widget_data']
                    parsed_json = json.loads(raw_json)

                    # Accès aux données de marché
                    instruments_data = parsed_json['extra_field']['collection']['data']['data']

                    # Accès aux labels des instruments
                    instrument_labels = parsed_json.get('instruments', [])
                    uuid_to_label = {inst['uuid']: inst['label'] for inst in instrument_labels}

                    print(f"🔍 Recherche parmi {len(instruments_data)} instruments...")

                    # Parcourir tous les instruments pour trouver celui avec le ticker correspondant
                    found_count = 0
                    for i, item in enumerate(instruments_data):
                        symbol_data = item['relationships']['symbol']['data']
                        symbol_uuid = symbol_data['id']
                        label = uuid_to_label.get(symbol_uuid, symbol_uuid)
                        url_instrument = item['relationships']['symbol']['links']['related']['href']

                        # Récupérer les détails de l'instrument pour vérifier le symbole
                        try:
                            response_instrument = requests.get(url_instrument, verify=False, timeout=10)
                            if response_instrument.status_code == 200:
                                data_instrument = response_instrument.json()
                                attributes = data_instrument['data']['attributes']

                                symbol_from_api = attributes.get('symbol')
                                symbol_id = attributes.get('drupal_internal__id')

                                # Vérifier si le symbole correspond au ticker recherché
                                if symbol_from_api and symbol_from_api.upper() == ticker.upper():
                                    print(f"✅ Ticker '{ticker}' trouvé -> Symbole_id: {symbol_id}, Libellé: {label}")
                                    return symbol_id
                                    
                                # Afficher la progression pour les recherches longues
                                found_count += 1
                                if found_count % 50 == 0:
                                    print(f"  🔍 {found_count}/{len(instruments_data)} instruments vérifiés...")

                        except Exception as e:
                            print(f"⚠️ Erreur lors de la récupération des détails pour {label}: {str(e)}")
                            continue

                    print(f"❌ Ticker '{ticker}' non trouvé dans la liste des instruments")
                    return None

            print("❌ Widget 'bourse_data_listing:marches-actions' non trouvé")
            return None

    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la liste des instruments: {str(e)}")
        return None

    return None

@with_build_id
def get_historical_data(ticker, from_date, to_date, build_id=None):
    """
    Récupère les données historiques d'un ticker pour une période donnée avec buildId dynamique
    """
    # Récupérer le Symbole_id correspondant au ticker avec buildId
    symbol_id = get_symbol_id_from_ticker(ticker, build_id=build_id)

    if not symbol_id:
        print(f"❌ Impossible de trouver le Symbole_id pour le ticker: {ticker}")
        return None

    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': f'https://www.casablanca-bourse.com/fr/instruments?instrument={symbol_id}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': 'application/vnd.api+json',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'Content-Type': 'application/vnd.api+json',
        'sec-ch-ua-mobile': '?0',
    }

    all_data = []
    offset = 0
    limit = 250

    print(f"📊 Récupération des données historiques pour {ticker} (ID: {symbol_id}) du {from_date} au {to_date}...")

    while True:
        params = [
            ('fields[instrument_history]', 'symbol,created,openingPrice,coursCourant,highPrice,lowPrice,cumulTitresEchanges,cumulVolumeEchange,totalTrades,capitalisation,coursAjuste,closingPrice,ratioConsolide'),
            ('fields[instrument]', 'symbol,libelleFR,libelleAR,libelleEN,emetteur_url,instrument_url'),
            ('fields[taxonomy_term--bourse_emetteur]', 'name'),
            ('include', 'symbol'),
            ('sort[date-seance][path]', 'created'),
            ('sort[date-seance][direction]', 'DESC'),
            ('filter[filter-historique-instrument-emetteur][condition][path]', 'symbol.codeSociete.meta.drupal_internal__target_id'),
            ('filter[filter-historique-instrument-emetteur][condition][value]', '-1'),
            ('filter[filter-historique-instrument-emetteur][condition][operator]', '='),
            ('filter[instrument-history-class][condition][path]', 'symbol.codeClasse.field_code'),
            ('filter[instrument-history-class][condition][value]', '1'),
            ('filter[instrument-history-class][condition][operator]', '='),
            ('filter[published]', '1'),
            ('page[offset]', str(offset)),
            ('page[limit]', str(limit)),
            ('filter[filter-date-start-vh][condition][path]', 'field_seance_date'),
            ('filter[filter-date-start-vh][condition][operator]', '>='),
            ('filter[filter-date-start-vh][condition][value]', from_date),
            ('filter[filter-date-end-vh][condition][path]', 'field_seance_date'),
            ('filter[filter-date-end-vh][condition][operator]', '<='),
            ('filter[filter-date-end-vh][condition][value]', to_date),
            ('filter[filter-historique-instrument-emetteur][condition][path]', 'symbol.meta.drupal_internal__target_id'),
            ('filter[filter-historique-instrument-emetteur][condition][operator]', '='),
            ('filter[filter-historique-instrument-emetteur][condition][value]', str(symbol_id)),
        ]

        try:
            response = requests.get(
                'https://www.casablanca-bourse.com/api/proxy/fr/api/bourse_data/instrument_history',
                params=params,
                headers=headers,
                verify=False,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()

                if 'data' in data and data['data']:
                    for item in data['data']:
                        attributes = item['attributes']

                        row = {
                            'Date': attributes.get('created'),
                            'Ouverture': attributes.get('openingPrice'),
                            'Clôture': attributes.get('closingPrice'),
                            'Dernier cours': attributes.get('coursCourant'),
                            'Plus haut': attributes.get('highPrice'),
                            'Plus bas': attributes.get('lowPrice'),
                            'Volume': attributes.get('cumulVolumeEchange'),
                            'Quantité échangée': attributes.get('cumulTitresEchanges'),
                            'Nombre de transactions': attributes.get('totalTrades'),
                            'Capitalisation': attributes.get('capitalisation'),
                            'Cours ajusté': attributes.get('coursAjuste'),
                            'Ratio consolidé': attributes.get('ratioConsolide')
                        }
                        all_data.append(row)

                    print(f"  ✅ Récupéré {len(data['data'])} enregistrements (offset: {offset})")

                    # Vérifier s'il y a plus de données
                    if len(data['data']) < limit:
                        break

                    offset += limit
                    time.sleep(0.5)  # Pause pour éviter de surcharger le serveur

                else:
                    print("  ℹ️ Aucune donnée supplémentaire trouvée")
                    break

            else:
                print(f"❌ Erreur {response.status_code} lors de la récupération des données")
                break

        except Exception as e:
            print(f"❌ Erreur lors de la requête: {str(e)}")
            break

    if all_data:
        df = pd.DataFrame(all_data)

        # Trier par date (croissant)
        df['Date'] = pd.to_datetime(df['Date'])
        df = df.sort_values('Date').reset_index(drop=True)

        print(f"✅ Données historiques récupérées avec succès: {len(df)} enregistrements")
        return df
    else:
        print("❌ Aucune donnée historique trouvée")
        return None


@with_build_id
def get_symbol_id_from_ticker_auto(ticker, build_id=None):
    """
    Version avec injection automatique du buildId
    """
    return get_symbol_id_from_ticker(ticker, build_id=build_id)

@with_build_id
def get_historical_data_auto(ticker, from_date, to_date, build_id=None):
    """
    Version avec injection automatique du buildId
    """
    return get_historical_data(ticker, from_date, to_date, build_id=build_id)

@with_build_id
# Fonction utilitaire pour rechercher plusieurs tickers
def get_multiple_symbol_ids(tickers, build_id=None):
    """
    Récupère les Symboles_id pour plusieurs tickers en une seule requête
    
    Args:
        tickers (list): Liste des tickers à rechercher
        build_id (str): BuildId dynamique
    
    Returns:
        dict: Dictionnaire {ticker: symbole_id}
    """
    
    results = {}
    
    for ticker in tickers:
        print(f"\n🔍 Recherche du ticker: {ticker}")
        symbol_id = get_symbol_id_from_ticker(ticker, build_id=build_id)
        if symbol_id:
            results[ticker] = symbol_id
        else:
            results[ticker] = None
            
        # Pause entre les recherches
        time.sleep(0.5)
    
    print(f"\n📊 Résultats: {len([v for v in results.values() if v])}/{len(tickers)} tickers trouvés")
    return results

# # Exemple d'utilisation
# if __name__ == "__main__":
#     # Méthode 1: Utilisation automatique (recommandée)
#     print("=== MÉTHODE 1: Utilisation automatique ===")
    
#     # Recherche d'un ticker spécifique
#     symbol_id = get_symbol_id_from_ticker_auto("AFM")
#     if symbol_id:
#         print(f"Symbole_id trouvé: {symbol_id}")
        
#         # Récupération des données historiques
#         df_historical = get_historical_data_auto("AFM", "2024-01-01", "2024-12-31")
        
#         if df_historical is not None:
#             print(f"\nAperçu des données historiques:")
#             print(df_historical.head())
#             print(f"\nPériode couverte: {df_historical['Date'].min()} à {df_historical['Date'].max()}")

#             # Sauvegarder en CSV
#             timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#             filename = f"historique_AFM_{timestamp}.csv"
#             df_historical.to_csv(filename, index=False, encoding='utf-8-sig')
#             print(f"📁 Données sauvegardées dans: {filename}")

#     # Méthode 2: Utilisation manuelle avec buildId explicite
#     print("\n=== MÉTHODE 2: Utilisation manuelle ===")
#     # from your_module import get_build_id_cached  # Adapter l'import
    
#     build_id = get_build_id_cached()
#     if build_id:
#         # Recherche de plusieurs tickers
#         tickers = ["AFM", "IAM", "ATW"]
#         results = get_multiple_symbol_ids(tickers, build_id=build_id)
        
#         print("\n📋 Résultats de la recherche multiple:")
#         for ticker, symbol_id in results.items():
#             status = "✅" if symbol_id else "❌"
#             print(f"  {status} {ticker}: {symbol_id}")
            
#         # Récupération des données historiques pour un ticker spécifique
#         if results.get("ATW"):
#             df_atw = get_historical_data("ATW", "2024-01-01", "2024-06-30", build_id=build_id)
#             if df_atw is not None:
#                 print(f"\n✅ Données ATW récupérées: {len(df_atw)} enregistrements")



## Plusieurs fonctions pour obtenir des informations sur les tickers et indexes

def get_market_data(marche=59, classes=[50]):
    """
    Récupère les données du marché principal de la Bourse de Casablanca

    Args:
        marche (int): ID du marché (59 pour le marché principal)
        classes (list): Liste des classes d'instruments

    Returns:
        pd.DataFrame: DataFrame avec toutes les données du marché
    """
    url = "https://www.casablanca-bourse.com/api/proxy/fr/api/bourse/dashboard/ticker"

    params = {
        'marche': marche,
        'class[]': classes
    }

    try:
        response = requests.get(url, params=params, verify=False, timeout=10)
        if response.status_code == 200:
            data = response.json()
            values = data['data']['values']

            # Transformation en DataFrame
            df = pd.DataFrame(values)

            # Renommer les colonnes pour plus de clarté
            column_mapping = {
                'field_best_ask_price': 'Meilleur prix vente',
                'field_best_ask_size': 'Quantité meilleur prix vente',
                'field_best_bid_price': 'Meilleur prix achat',
                'field_best_bid_size': 'Quantité meilleur prix achat',
                'field_capitalisation': 'Capitalisation',
                'field_closing_price': 'Prix clôture',
                'field_cours_ajuste': 'Cours ajusté',
                'field_cours_courant': 'Cours courant',
                'field_cumul_titres_echanges': 'Quantité échangée',
                'field_cumul_volume_echange': 'Volume échangé',
                'field_difference': 'Différence',
                'field_etat_cot_val': 'Statut',
                'field_high_price': 'Plus haut',
                'field_low_price': 'Plus bas',
                'field_opening_price': 'Ouverture',
                'field_static_reference_price': 'Prix référence',
                'field_total_trades': 'Nombre transactions',
                'field_var_veille': 'Variation %',
                'label': 'Nom',
                'ticker': 'Symbole',
                'sous_secteur': 'Secteur'
            }

            df = df.rename(columns=column_mapping)

            print(f"✅ Données récupérées: {len(df)} instruments")
            return df
        else:
            print(f"❌ Erreur {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Erreur: {str(e)}")
        return None

def get_top_gainers(limit=10):
    """
    Retourne les instruments avec la plus forte hausse

    Args:
        limit (int): Nombre d'instruments à retourner

    Returns:
        pd.DataFrame: Top des instruments en hausse
    """
    df = get_market_data()
    if df is not None:
        # Convertir la variation en numérique et filtrer les valeurs manquantes
        df['Variation %'] = pd.to_numeric(df['Variation %'], errors='coerce')
        gainers = df[df['Variation %'] > 0].nlargest(limit, 'Variation %')
        return gainers[['Symbole', 'Nom', 'Cours courant', 'Variation %', 'Volume échangé']]
    return None

def get_top_losers(limit=10):
    """
    Retourne les instruments avec la plus forte baisse

    Args:
        limit (int): Nombre d'instruments à retourner

    Returns:
        pd.DataFrame: Top des instruments en baisse
    """
    df = get_market_data()
    if df is not None:
        df['Variation %'] = pd.to_numeric(df['Variation %'], errors='coerce')
        losers = df[df['Variation %'] < 0].nsmallest(limit, 'Variation %')
        return losers[['Symbole', 'Nom', 'Cours courant', 'Variation %', 'Volume échangé']]
    return None

def get_most_active(limit=10, by='volume'):
    """
    Retourne les instruments les plus actifs

    Args:
        limit (int): Nombre d'instruments à retourner
        by (str): Critère ('volume' ou 'transactions')

    Returns:
        pd.DataFrame: Instruments les plus actifs
    """
    df = get_market_data()
    if df is not None:
        if by == 'volume':
            df['Volume échangé'] = pd.to_numeric(df['Volume échangé'], errors='coerce')
            active = df.nlargest(limit, 'Volume échangé')
        else:  # par transactions
            df['Nombre transactions'] = pd.to_numeric(df['Nombre transactions'], errors='coerce')
            active = df.nlargest(limit, 'Nombre transactions')

        return active[['Symbole', 'Nom', 'Cours courant', 'Volume échangé', 'Nombre transactions']]
    return None

def get_sector_performance():
    """
    Analyse la performance par secteur

    Returns:
        pd.DataFrame: Performance agrégée par secteur
    """
    df = get_market_data()
    if df is not None:
        df['Variation %'] = pd.to_numeric(df['Variation %'], errors='coerce')
        df['Capitalisation'] = pd.to_numeric(df['Capitalisation'], errors='coerce')

        sector_perf = df.groupby('Secteur').agg({
            'Variation %': 'mean',
            'Capitalisation': 'sum',
            'Symbole': 'count'
        }).round(2)

        sector_perf = sector_perf.rename(columns={
            'Variation %': 'Variation moyenne %',
            'Capitalisation': 'Capitalisation totale',
            'Symbole': "Nombre d'instruments"
        })

        return sector_perf.sort_values('Variation moyenne %', ascending=False)
    return None

def get_instrument_details(ticker):
    """
    Récupère les détails d'un instrument spécifique

    Args:
        ticker (str): Symbole de l'instrument

    Returns:
        dict: Détails de l'instrument
    """
    df = get_market_data()
    if df is not None:
        instrument = df[df['Symbole'] == ticker.upper()]
        if not instrument.empty:
            return instrument.iloc[0].to_dict()
        else:
            print(f"❌ Instrument '{ticker}' non trouvé")
            return None
    return None

def get_market_summary():
    """
    Fournit un résumé général du marché

    Returns:
        dict: Statistiques du marché
    """
    df = get_market_data()
    if df is not None:
        # Convertir les colonnes numériques
        numeric_cols = ['Cours courant', 'Variation %', 'Volume échangé', 'Capitalisation']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        summary = {
            'Nombre total instruments': len(df),
            'Instruments en hausse': len(df[df['Variation %'] > 0]),
            'Instruments en baisse': len(df[df['Variation %'] < 0]),
            'Instruments stables': len(df[df['Variation %'] == 0]),
            'Variation moyenne (%)': df['Variation %'].mean(),
            'Volume total échangé': df['Volume échangé'].sum(),
            'Capitalisation totale': df['Capitalisation'].sum(),
            'Top 3 secteurs': df['Secteur'].value_counts().head(3).to_dict()
        }

        return summary
    return None

def get_technical_indicators(ticker):
    """
    Calcule des indicateurs techniques basiques pour un instrument

    Args:
        ticker (str): Symbole de l'instrument

    Returns:
        dict: Indicateurs techniques
    """
    details = get_instrument_details(ticker)
    if details:
        cours_courant = float(details.get('Cours courant', 0))
        ouverture = float(details.get('Ouverture', 0))
        plus_haut = float(details.get('Plus haut', 0))
        plus_bas = float(details.get('Plus bas', 0))

        # Calculs basiques
        variation_jour = ((cours_courant - ouverture) / ouverture * 100) if ouverture else 0
        amplitude = ((plus_haut - plus_bas) / plus_bas * 100) if plus_bas else 0

        indicators = {
            'Support (Plus bas)': plus_bas,
            'Résistance (Plus haut)': plus_haut,
            'Amplitude journée (%)': round(amplitude, 2),
            'Variation vs ouverture (%)': round(variation_jour, 2),
            'Ecart prix achat/vente': float(details.get('Meilleur prix vente', 0)) - float(details.get('Meilleur prix achat', 0)),
            'Ratio volume/transactions': float(details.get('Volume échangé', 0)) / float(details.get('Nombre transactions', 1)) if details.get('Nombre transactions') else 0
        }

        return indicators
    return None

def export_market_data(format='csv', filename=None):
    """
    Exporte les données du marché dans différents formats

    Args:
        format (str): Format d'export ('csv', 'excel', 'json')
        filename (str): Nom du fichier (optionnel)
    """
    df = get_market_data()
    if df is not None:
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"bourse_casablanca_{timestamp}"

        if format == 'csv':
            filename += '.csv'
            df.to_csv(filename, index=False, encoding='utf-8-sig')
        elif format == 'excel':
            filename += '.xlsx'
            df.to_excel(filename, index=False)
        elif format == 'json':
            filename += '.json'
            df.to_json(filename, orient='records', indent=2)

        print(f"✅ Données exportées: {filename}")
        return filename
    return None

# # Exemples d'utilisation
# if __name__ == "__main__":
#     # 1. Récupérer toutes les données du marché
#     print("=== DONNÉES COMPLÈTES DU MARCHÉ ===")
#     df_market = get_market_data()
#     if df_market is not None:
#         print(df_market.head())

#     # 2. Top des valeurs en hausse
#     print("\n=== TOP 5 DES HAUSSIERS ===")
#     gainers = get_top_gainers(5)
#     if gainers is not None:
#         print(gainers)

#     # 3. Top des valeurs en baisse
#     print("\n=== TOP 5 DES BAISSIERS ===")
#     losers = get_top_losers(5)
#     if losers is not None:
#         print(losers)

#     # 4. Instruments les plus actifs
#     print("\n=== TOP 5 DES PLUS ACTIFS (VOLUME) ===")
#     active = get_most_active(5, 'volume')
#     if active is not None:
#         print(active)

#     # 5. Performance par secteur
#     print("\n=== PERFORMANCE PAR SECTEUR ===")
#     sectors = get_sector_performance()
#     if sectors is not None:
#         print(sectors)

#     # 6. Détails d'un instrument spécifique
#     print("\n=== DÉTAILS INSTRUMENT 'ADI' ===")
#     adi_details = get_instrument_details('ADI')
#     if adi_details:
#         print(f"Nom: {adi_details.get('Nom')}")
#         print(f"Cours: {adi_details.get('Cours courant')}")
#         print(f"Variation: {adi_details.get('Variation %')}%")

#     # 7. Résumé du marché
#     print("\n=== RÉSUMÉ DU MARCHÉ ===")
#     summary = get_market_summary()
#     if summary:
#         for key, value in summary.items():
#             print(f"{key}: {value}")

#     # 8. Indicateurs techniques
#     print("\n=== INDICATEURS TECHNIQUES 'ADI' ===")
#     indicators = get_technical_indicators('ADI')
#     if indicators:
#         for key, value in indicators.items():
#             print(f"{key}: {value}")

#     # 9. Export des données
#     print("\n=== EXPORT DES DONNÉES ===")
#     export_market_data('csv')



# Cette fonction permet de récupérer les données sommaires sur les volumes

@with_build_id
def get_volume_overview(build_id=None):
    """
    Récupère et structure les données de volume de la Bourse de Casablanca
    pour la séance en cours, à partir du widget dynamique "transaction-volume".

    Retourne cinq tableaux pandas :
    - df_global : Volume global de la séance.
    - df_top : Top 10 des instruments les plus actifs.
    - df_central : Détail du marché central par classe d’actif.
    - df_blocs : Détail du marché de blocs par classe d’actif.
    - df_autres : Volumes des autres segments (introductions, transferts, etc.).

    Returns:
        tuple:
            df_global (pd.DataFrame): Volume global.
            df_top (pd.DataFrame): Instruments les plus actifs.
            df_central (pd.DataFrame): Marché central.
            df_blocs (pd.DataFrame): Marché de blocs.
            df_autres (pd.DataFrame): Autres marchés.
    """
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'x-vactory-data-loader': f'/_next/data/{build_id}/fr/data/donnees-de-marche/volume.json?slug=data&slug=donnees-de-marche&slug=volume',
        'Referer': 'https://www.casablanca-bourse.com/fr/data/donnees-de-marche/volume',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
    }

    params = {
        'slug': ['data', 'donnees-de-marche', 'volume'],
    }

    response = requests.get(
        f'https://www.casablanca-bourse.com/_next/data/{build_id}/fr/data/donnees-de-marche/volume.json',
        params=params,
        headers=headers,
        verify=False
    )

    data = response.json()
    paragraphs = data.get('pageProps', {}).get('node', {}).get('field_vactory_paragraphs', [])

    for p in paragraphs:
        component = p.get('field_vactory_component', {})
        if component.get('widget_id') != "bourse_dynamic_field:transaction-volume":
            continue

        widget_data_str = component.get('widget_data')
        if not widget_data_str:
            continue

        widget_data = json.loads(widget_data_str)
        components = widget_data.get('components', [])
        if not components:
            continue

        comp = components[0]

        # Volume global
        volume_global = comp.get('volume_global', {})
        volume_value = volume_global.get('volume')
        df_global = pd.DataFrame([{
            "Libellé": volume_global.get('title'),
            "Montant (MAD)": format_mad(volume_value)
        }])

        # Top 10 instruments
        top_volumes = comp.get('best_volume', {}).get('volumes', [])
        df_top = pd.DataFrame([
            {
                "Instrument": item['instrument'],
                "Volume (MAD)": format_mad(item['volume'])
            } for item in top_volumes
        ])

        # Volumes par marché
        market_rows = []
        for market in comp.get('marches_volume', {}).get('values', []):
            label = market['label']
            if market.get('volume_by_classes'):
                for cls in market['volume_by_classes']:
                    market_rows.append({
                        "Marché": label,
                        "Classe": cls['label'],
                        "Volume classe (MAD)": format_mad(cls['volume'])
                    })
            else:
                market_rows.append({
                    "Marché": label,
                    "Classe": label,
                    "Volume classe (MAD)": format_mad(market['total_volume'])
                })

        df_market = pd.DataFrame(market_rows)
        df_central = df_market[df_market["Marché"] == "MARCHE CENTRAL"][["Classe", "Volume classe (MAD)"]]
        df_blocs = df_market[df_market["Marché"] == "MARCHE DE BLOCS"][["Classe", "Volume classe (MAD)"]]
        df_autres = df_market[~df_market["Marché"].isin(["MARCHE CENTRAL", "MARCHE DE BLOCS"])]
        df_autres = df_autres[["Marché", "Volume classe (MAD)"]].rename(columns={"Marché": "Classe"})

        return df_global, df_top, df_central, df_blocs, df_autres

    return None, None, None, None, None


# df_global, df_top, df_central, df_blocs, df_autres = get_volume_overview()

# if df_global is not None:
#     print("\nTABLEAU 1 : Volume global")
#     print(df_global.to_string(index=False))

#     print("\nTABLEAU 2 : Top 10 instruments les plus actifs")
#     print(df_top.to_string(index=False))

#     print("\nTABLEAU 3A : MARCHE CENTRAL")
#     print(df_central.to_string(index=False))

#     print("\nTABLEAU 3B : MARCHE DE BLOCS")
#     print(df_blocs.to_string(index=False))

#     print("\nTABLEAU 3C : AUTRES MARCHÉS")
#     print(df_autres.to_string(index=False))
# else:
#     print("Aucune donnée disponible.")


# Fonction pour récupérer les données de volume de la Bourse de Casablanca entre deux dates
def get_volume_data(from_date, to_date, formatted=True):
    """
    Récupère les données de volume de la Bourse de Casablanca entre deux dates
    
    Args:
        from_date (str): Date de début au format 'YYYY-MM-DD'
        to_date (str): Date de fin au format 'YYYY-MM-DD'
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        pd.DataFrame: DataFrame avec les données de volume
    """
    
    # Vérification du format des dates
    try:
        datetime.strptime(from_date, '%Y-%m-%d')
        datetime.strptime(to_date, '%Y-%m-%d')
    except ValueError:
        print("Erreur: Le format des dates doit être 'YYYY-MM-DD'")
        return None
    
    all_data = []
    offset = 0
    limit = 250
    
    # Headers pour les requêtes API
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.casablanca-bourse.com/fr/historique-du-volume',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': 'application/vnd.api+json',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'Content-Type': 'application/vnd.api+json',
        'sec-ch-ua-mobile': '?0',
    }
    
    print(f"Récupération des données de volume du {from_date} au {to_date}...")
    
    while True:
        try:
            # Paramètres de la requête
            params = [
                ('fields[bourse_data--volume_history]', 'field_seance_date,field_volume_marche_central,field_volume_marche_blocs,field_volume_introductions,field_volume_offres_publiques,field_volume_transferts,field_volume_apports,field_volume_aug_capital,field_volume_pret_titres,field_volume_total'),
                ('sort[date-seance][path]', 'field_seance_date'),
                ('sort[date-seance][direction]', 'DESC'),
                ('filter[published]', '1'),
                ('page[offset]', str(offset)),
                ('page[limit]', str(limit)),
                ('filter[filter-date-start-vh-select][condition][path]', 'field_seance_date'),
                ('filter[filter-date-start-vh-select][condition][operator]', '>='),
                ('filter[filter-date-start-vh-select][condition][value]', from_date),
                ('filter[filter-date-end-vh-select][condition][path]', 'field_seance_date'),
                ('filter[filter-date-end-vh-select][condition][operator]', '<='),
                ('filter[filter-date-end-vh-select][condition][value]', to_date),
            ]
            
            # Requête à l'API
            response = requests.get(
                'https://www.casablanca-bourse.com/api/proxy/fr/api/bourse_data/volume_history',
                params=params,
                headers=headers,
                verify=False,
                timeout=30
            )
            
            # Vérification du statut de la réponse
            if response.status_code != 200:
                print(f"Erreur API: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            
            # Vérification de la présence de données
            if 'data' not in data or not data['data']:
                print("  Aucune donnée supplémentaire trouvée")
                break
            
            # Extraction des données
            for item in data['data']:
                attributes = item.get('attributes', {})
                row_data = {
                    'Séance': attributes.get('field_seance_date', ''),
                    'Volume Marché Central': float(attributes.get('field_volume_marche_central', 0) or 0),
                    'Volume Marché De Blocs': float(attributes.get('field_volume_marche_blocs', 0) or 0),
                    'Volume Introductions': float(attributes.get('field_volume_introductions', 0) or 0),
                    'Volume Offres Publiques': float(attributes.get('field_volume_offres_publiques', 0) or 0),
                    'Volume Transferts': float(attributes.get('field_volume_transferts', 0) or 0),
                    'Volume Apports': float(attributes.get('field_volume_apports', 0) or 0),
                    'Volume Augmentations du Capital': float(attributes.get('field_volume_aug_capital', 0) or 0),
                    'Volume prêt titre': float(attributes.get('field_volume_pret_titres', 0) or 0),
                    'Total': float(attributes.get('field_volume_total', 0) or 0)
                }
                all_data.append(row_data)
            
            print(f"  Récupéré {len(data['data'])} enregistrements (offset: {offset})")
            
            # Vérification si on a récupéré toutes les données
            if len(data['data']) < limit:
                break
                
            # Incrémentation de l'offset et pause
            offset += limit
            time.sleep(0.5)  # Pause pour éviter de surcharger le serveur
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête: {e}")
            break
        except Exception as e:
            print(f"Erreur inattendue: {e}")
            break
    
    if all_data:
        # Création du DataFrame
        df = pd.DataFrame(all_data)
        
        # Conversion de la colonne Séance en datetime et tri
        df['Séance'] = pd.to_datetime(df['Séance'])
        df = df.sort_values('Séance').reset_index(drop=True)
        
        # Formater les colonnes numériques si demandé
        if formatted:
            volume_columns = [
                'Volume Marché Central', 'Volume Marché De Blocs', 'Volume Introductions',
                'Volume Offres Publiques', 'Volume Transferts', 'Volume Apports',
                'Volume Augmentations du Capital', 'Volume prêt titre', 'Total'
            ]
            
            for col in volume_columns:
                df[col] = df[col].apply(format_number_french)
        
        print(f"✅ Données de volume récupérées avec succès: {len(df)} enregistrements")
        return df
    else:
        print("❌ Aucune donnée de volume trouvée")
        return None

# # Exemple d'utilisation
# if __name__ == "__main__":
#     # Récupérer les données pour une période spécifique (formatées)
#     df_volume = get_volume_data('2024-01-01', '2025-01-31', formatted=True)
    
#     if df_volume is not None:
#         print("\nAperçu des données de volume (formatées):")
#         print(df_volume.head())
#         print(f"\nPériode couverte: {df_volume['Séance'].min()} à {df_volume['Séance'].max()}")
#         print(f"\nColonnes disponibles: {list(df_volume.columns)}")
        
#         # Sauvegarder en CSV
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"volume_data_{timestamp}.csv"
#         df_volume.to_csv(filename, index=False, encoding='utf-8-sig')
#         print(f"📁 Données sauvegardées dans: {filename}")
#     else:
#         print("Aucune donnée récupérée")

# # Récupérer les données non formatées pour les calculs
# df_raw = get_volume_data('2024-01-01', '2025-10-07', formatted=False)

# # Récupérer les données formatées pour l'affichage
# df_formatted = get_volume_data('2024-01-01', '2025-10-07', formatted=True)

# if df_formatted is not None:
#     # Afficher un aperçu formaté
#     print(df_formatted.head())
    
#     # Sauvegarder
#     # df.to_csv('volume_data.csv', index=False)



# Fonction pour récupérer les données de capitalisation de la Bourse de Casablanca entre deux dates

def get_capitalization_data(from_date, to_date):
    """
    Récupère les données de capitalisation de la Bourse de Casablanca entre deux dates
    
    Args:
        from_date (str): Date de début au format 'YYYY-MM-DD'
        to_date (str): Date de fin au format 'YYYY-MM-DD'
    
    Returns:
        pd.DataFrame: DataFrame avec les données de capitalisation (Séance, Capitalisation (MAD))
    """
    
    # Vérification du format des dates
    try:
        datetime.strptime(from_date, '%Y-%m-%d')
        datetime.strptime(to_date, '%Y-%m-%d')
    except ValueError:
        print("Erreur: Le format des dates doit être 'YYYY-MM-DD'")
        return None
    
    all_data = []
    offset = 0
    limit = 250
    
    # Headers pour les requêtes API
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': f'https://www.casablanca-bourse.com/fr/historique-de-la-capitalisation?datestart={from_date}&dateend={to_date}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': 'application/vnd.api+json',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'Content-Type': 'application/vnd.api+json',
        'sec-ch-ua-mobile': '?0',
    }
    
    print(f"Récupération des données de capitalisation du {from_date} au {to_date}...")
    
    while True:
        try:
            # Paramètres de la requête
            params = [
                ('fields[bourse_data--capitalisation_history]', 'field_seance_date,field_capitalisation_global'),
                ('sort[date-seance][path]', 'field_seance_date'),
                ('sort[date-seance][direction]', 'DESC'),
                ('filter[published]', '1'),
                ('page[offset]', str(offset)),
                ('page[limit]', str(limit)),
                ('filter[filter-date-start-vh][condition][path]', 'field_seance_date'),
                ('filter[filter-date-start-vh][condition][operator]', '>='),
                ('filter[filter-date-start-vh][condition][value]', from_date),
                ('filter[filter-date-end-vh][condition][path]', 'field_seance_date'),
                ('filter[filter-date-end-vh][condition][operator]', '<='),
                ('filter[filter-date-end-vh][condition][value]', to_date),
            ]
            
            # Requête à l'API
            response = requests.get(
                'https://www.casablanca-bourse.com/api/proxy/fr/api/bourse_data/capitalisation_history',
                params=params,
                headers=headers,
                verify=False,
                timeout=30
            )
            
            # Vérification du statut de la réponse
            if response.status_code != 200:
                print(f"Erreur API: {response.status_code} - {response.text}")
                break
            
            data = response.json()
            
            # Vérification de la présence de données
            if 'data' not in data or not data['data']:
                print("  Aucune donnée supplémentaire trouvée")
                break
            
            # Extraction des données
            for item in data['data']:
                attributes = item.get('attributes', {})
                row_data = {
                    'Séance': attributes.get('field_seance_date', ''),
                    'Capitalisation (MAD)': float(attributes.get('field_capitalisation_global', 0) or 0)
                }
                all_data.append(row_data)
            
            print(f"  Récupéré {len(data['data'])} enregistrements (offset: {offset})")
            
            # Vérification si on a récupéré toutes les données
            if len(data['data']) < limit:
                break
                
            # Incrémentation de l'offset et pause
            offset += limit
            time.sleep(0.5)  # Pause pour éviter de surcharger le serveur
            
        except requests.exceptions.RequestException as e:
            print(f"Erreur de requête: {e}")
            break
        except Exception as e:
            print(f"Erreur inattendue: {e}")
            break
    
    if all_data:
        # Création du DataFrame
        df = pd.DataFrame(all_data)
        
        # Conversion de la colonne Séance en datetime et tri
        df['Séance'] = pd.to_datetime(df['Séance'])
        df = df.sort_values('Séance').reset_index(drop=True)
        
        # Créer une colonne formatée pour l'affichage
        df['Capitalisation Formatée'] = df['Capitalisation (MAD)'].apply(format_number_french)
        
        print(f"✅ Données de capitalisation récupérées avec succès: {len(df)} enregistrements")
        return df
    else:
        print("❌ Aucune donnée de capitalisation trouvée")
        return None

# # Exemple d'utilisation
# if __name__ == "__main__":
#     # Récupérer les données pour une période spécifique
#     df_capitalization = get_capitalization_data('2024-01-01', '2025-11-08')
    
#     if df_capitalization is not None:
#         print("\nAperçu des données de capitalisation:")
        
#         # Afficher avec le format français
#         display_columns = ['Séance', 'Capitalisation Formatée']
#         print(df_capitalization[display_columns].head())
        
#         print(f"\nPériode couverte: {df_capitalization['Séance'].min()} à {df_capitalization['Séance'].max()}")
#         print(f"\nColonnes disponibles: {list(df_capitalization.columns)}")
        
#         # Statistiques descriptives avec format français
#         print(f"\nStatistiques de capitalisation:")
#         stats = df_capitalization['Capitalisation (MAD)'].describe()
        
#         print(f"Count: {format_number_french(stats['count'])}")
#         print(f"Mean: {format_number_french(stats['mean'])}")
#         print(f"Std: {format_number_french(stats['std'])}")
#         print(f"Min: {format_number_french(stats['min'])}")
#         print(f"25%: {format_number_french(stats['25%'])}")
#         print(f"50%: {format_number_french(stats['50%'])}")
#         print(f"75%: {format_number_french(stats['75%'])}")
#         print(f"Max: {format_number_french(stats['max'])}")
        
#         # Sauvegarder en CSV (garder les deux colonnes)
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"capitalization_data_{timestamp}.csv"
#         df_capitalization.to_csv(filename, index=False, encoding='utf-8-sig')
#         print(f"📁 Données sauvegardées dans: {filename}")
        
#         # Option: Afficher un échantillon formaté
#         print(f"\nExemple de valeurs formatées:")
#         sample = df_capitalization[['Séance', 'Capitalisation Formatée']].head(3)
#         for _, row in sample.iterrows():
#             print(f"  {row['Séance'].strftime('%Y-%m-%d')}: {row['Capitalisation Formatée']} MAD")
#     else:
#         print("Aucune donnée récupérée")

# Récupérer les données
# df = get_capitalization_data('2024-01-01', '2024-12-31')

# # Afficher les premières lignes
# print(df.head())

# # Filtrer pour une période spécifique
# df_2024 = df[df['Séance'].dt.year == 2024]

# # Sauvegarder
# df.to_csv('capitalization.csv', index=False)



# Fonction pour récupérer de façon sommaire les données de capitalisation de la Bourse de Casablanca
@with_build_id
def get_capitalization_overview(formatted=True, build_id=None):
    """
    Récupère de façon sommaire les données de capitalisation de la Bourse de Casablanca
    
    Args:
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        dict: Dictionnaire contenant trois DataFrames:
            - 'global_cap': Capitalisation globale
            - 'top_10': Dix meilleures capitalisations  
            - 'sectorial': Capitalisation sectorielle
    """
    
    # Headers pour les requêtes API
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'x-vactory-data-loader': f'/_next/data/{build_id}/fr/capitalisation.json?slug=capitalisation',
        'Referer': 'https://www.casablanca-bourse.com/fr/capitalisation',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
    }

    params = {
        'slug': 'capitalisation',
    }

    try:
        print("Récupération des données de capitalisation...")
        
        response = requests.get(
            f'https://www.casablanca-bourse.com/_next/data/{build_id}/fr/capitalisation.json',
            params=params,
            headers=headers,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"Erreur API: {response.status_code}")
            return None

        data = response.json()
        
        # Extraction des données du widget
        paragraphs = data['pageProps']['node']['field_vactory_paragraphs']
        
        for block in paragraphs:
            widget_id = block.get('field_vactory_component', {}).get('widget_id', '')
            if widget_id == 'bourse_dynamic_field:capitalisations':
                raw_json = block['field_vactory_component']['widget_data']
                parsed_data = json.loads(raw_json)
                components = parsed_data['components'][0]
                
                # 1. Capitalisation globale
                global_cap_data = components.get('capitalisation_global', {})
                seance_data = components.get('seance', {})
                
                capitalisation_value = float(global_cap_data.get('value', 0) or 0)
                
                global_cap_df = pd.DataFrame([{
                    'Séance': seance_data.get('seance', ''),
                    'État de séance': seance_data.get('etat_seance', ''),
                    'Heure ouverture': seance_data.get('heure_ouverture', ''),
                    'Capitalisation globale (MAD)': format_number_french(capitalisation_value) if formatted else capitalisation_value
                }])
                
                # 2. Top 10 des capitalisations
                top_cap_data = components.get('top_capitalisations', {}).get('capitalisations', [])
                top_10_list = []
                
                for i, item in enumerate(top_cap_data, 1):
                    capitalisation = float(item.get('field_capitalisation', 0) or 0)
                    dernier_cours = float(item.get('field_cours_courant', 0) or 0)
                    volume = float(item.get('field_cumul_volume_echange', 0) or 0)
                    
                    top_10_list.append({
                        'Rang': i,
                        'Société': item.get('label', ''),
                        'Ticker': item.get('ticker', ''),
                        'Secteur': item.get('sous_secteur', ''),
                        'Capitalisation (MAD)': format_number_french(capitalisation) if formatted else capitalisation,
                        'Dernier cours': format_number_french(dernier_cours) if formatted else dernier_cours,
                        'Variation': float(item.get('field_difference', 0) or 0),
                        'Volume échangé': format_number_french(volume) if formatted else volume
                    })
                
                top_10_df = pd.DataFrame(top_10_list)
                
                # 3. Capitalisation sectorielle
                sectorial_data = components.get('capitalisation_sectoriel', {}).get('capitalisations', [])
                sectorial_list = []
                
                for item in sectorial_data:
                    capitalisation = float(item.get('capitalisation', 0) or 0)
                    pourcentage = float(item.get('pourcentage', 0) or 0)
                    
                    sectorial_list.append({
                        'Secteur': item.get('sous_secteur', ''),
                        'Pourcentage': f"{pourcentage:.2f}%" if formatted else pourcentage,
                        'Capitalisation (MAD)': format_number_french(capitalisation) if formatted else capitalisation,
                        'Label': item.get('label', '')
                    })
                
                sectorial_df = pd.DataFrame(sectorial_list)
                
                print("✅ Données de capitalisation récupérées avec succès")
                
                return {
                    'global_cap': global_cap_df,
                    'top_10': top_10_df,
                    'sectorial': sectorial_df
                }
        
        print("❌ Données de capitalisation non trouvées dans la réponse")
        return None
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données: {e}")
        return None

# # Exemple d'utilisation
# if __name__ == "__main__":
#     # Récupérer les données formatées (par défaut)
#     data_formatted = get_capitalization_overview(formatted=True)
    
#     # Récupérer les données brutes
#     data_raw = get_capitalization_overview(formatted=False)
    
#     if data_formatted is not None:
#         global_cap, top_10, sectorial = data_formatted['global_cap'], data_formatted['top_10'], data_formatted['sectorial']
        
#         print("\n" + "="*50)
#         print("CAPITALISATION GLOBALE (FORMATÉE)")
#         print("="*50)
#         print(global_cap)
        
#         print("\n" + "="*50)
#         print("TOP 10 DES CAPITALISATIONS (FORMATÉES)")
#         print("="*50)
#         print(top_10.head(10))
        
#         print("\n" + "="*50)
#         print("CAPITALISATION SECTORIELLE (FORMATÉE)")
#         print("="*50)
#         print(sectorial)
        
#         # Sauvegarder en CSV
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
#         global_cap.to_csv(f"capitalisation_globale_{timestamp}.csv", index=False, encoding='utf-8-sig')
#         top_10.to_csv(f"top_10_capitalisations_{timestamp}.csv", index=False, encoding='utf-8-sig')
#         sectorial.to_csv(f"capitalisation_sectorielle_{timestamp}.csv", index=False, encoding='utf-8-sig')
        
#         print(f"\n📁 Données sauvegardées avec le timestamp: {timestamp}")
        
#     else:
#         print("Aucune donnée récupérée")

# # get_capitalization_overview(formatted=False)



# 14 fonctions importantes
# 1. format_number_french(number): Formate un nombre avec des espaces pour les milliers et une virgule pour les décimales ex Format français : 48 364 865,45
# 2. get_all_indices_overview(formatted=True) : Récupère un aperçu de tous les indices de la Bourse de Casablanca
# 3. extract_index_code(index_url) Extrait le code de l'indice à partir de l'URL
# 4. format_indices_to_dataframe(indices_data, formatted=True) Convertit les données des indices en DataFrame pandas avec URL complète et index_code
# 5. get_indices_list_with_capitalization(formatted=True) Retourne la liste complète des indices avec leur code et capitalisation
# 6. get_main_indices(formatted=True) Récupère uniquement les principaux indices (MASI, MASI 20, MASI ESG, MASI Mid and Small Cap)
# 7. get_sector_indices(formatted=True) #Récupère uniquement les indices sectoriels
# 8. get_index_by_name(index_name, formatted=True) #Récupère les données d'un indice spécifique par son nom
# 9. get_index_by_code(index_code, formatted=True) #Récupère les données d'un indice spécifique par son code
# 10. get_top_performers(n=5, period='veille', formatted=True) #Récupère les indices ayant les meilleures performances
# 11. get_worst_performers(n=5, period='veille', formatted=True) #Récupère les indices ayant les moins bonnes performances
# 12. get_market_summary(formatted=True) # Récupère un résumé du marché avec les indicateurs clés
# 13. get_available_indices_for_composition() #Retourne la liste des indices disponibles pour récupérer la composition avec leur code et capitalisation, triés par capitalisation décroissante
# 14. export_indices_to_csv(indices_data, filename=None) #Exporte les données des indices vers un fichier CSV

def get_all_indices_overview(formatted=True):
    """
    Récupère un aperçu de tous les indices de la Bourse de Casablanca
    
    Args:
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        dict: Dictionnaire avec les données de tous les indices groupés par catégorie
    """
    
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'Referer': 'https://www.casablanca-bourse.com/fr/live-market/marche-cash/indices',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'Accept': 'application/vnd.api+json',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'Content-Type': 'application/vnd.api+json',
        'sec-ch-ua-mobile': '?0',
    }

    try:
        print("Récupération de l'aperçu de tous les indices...")
        
        response = requests.get(
            'https://www.casablanca-bourse.com/api/proxy/fr/api/bourse/dashboard/grouped_index_watch',
            headers=headers,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Erreur API: {response.status_code}")
            return None

        data = response.json()
        
        if 'data' not in data:
            print("❌ Aucune donnée trouvée")
            return None
        
        print(f"✅ Aperçu des indices récupéré avec succès: {len(data['data'])} catégories")
        return data['data']
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'aperçu des indices: {e}")
        return None

def extract_index_code(index_url):
    """
    Extrait le code de l'indice à partir de l'URL
    
    Args:
        index_url (str): URL de l'indice (ex: "/fr/live-market/indices/MASI")
    
    Returns:
        str: Code de l'indice (ex: "MASI")
    """
    if not index_url:
        return ""
    
    # Extraire la dernière partie de l'URL après le dernier '/'
    return index_url.split('/')[-1]

def format_indices_to_dataframe(indices_data, formatted=True):
    """
    Convertit les données des indices en DataFrame pandas avec URL complète et index_code
    
    Args:
        indices_data (list): Données des indices retournées par get_all_indices_overview()
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        pd.DataFrame: DataFrame avec tous les indices
    """
    
    if not indices_data:
        return None
    
    all_indices = []
    
    for category in indices_data:
        category_name = category.get('title', 'Non catégorisé')
        
        for item in category.get('items', []):
            # Extraire l'index_code depuis l'URL
            index_url = item.get('index_url', '')
            index_code = extract_index_code(index_url)
            
            # Construire l'URL complète
            full_url = f"https://www.casablanca-bourse.com{index_url}" if index_url else ""
            
            # Préparation des données
            capitalisation = float(item.get('field_market_capitalisation', 0) or 0)
            valeur_indice = float(item.get('field_index_value', 0) or 0)
            plus_bas = float(item.get('field_index_low_value', 0) or 0)
            plus_haut = float(item.get('field_index_high_value', 0) or 0)
            cours_veille = float(item.get('veille', 0) or 0)
            diviseur = float(item.get('field_divisor', 0) or 0)
            
            index_data = {
                'Catégorie': category_name,
                'Indice': item.get('index', ''),
                'Code_Index': index_code,
                'URL_Complete': full_url,
                'URL_Relative': index_url,
                'Capitalisation (MAD)': format_number_french(capitalisation) if formatted else capitalisation,
                'Valeur indice': format_number_french(valeur_indice) if formatted else valeur_indice,
                'Plus bas': format_number_french(plus_bas) if formatted else plus_bas,
                'Plus haut': format_number_french(plus_haut) if formatted else plus_haut,
                'Cours veille': format_number_french(cours_veille) if formatted else cours_veille,
                'Variation annuelle (%)': float(item.get('field_var_year', 0) or 0),
                'Variation veille (%)': float(item.get('field_var_veille', 0) or 0),
                'Diviseur': format_number_french(diviseur) if formatted else diviseur,
                'Heure transaction': item.get('field_transact_time', ''),
                'Capitalisation_num': capitalisation,  # Pour le tri
                'Valeur_indice_num': valeur_indice     # Pour le tri
            }
            all_indices.append(index_data)
    
    df = pd.DataFrame(all_indices)
    print(f"✅ DataFrame créé avec {len(df)} indices")
    return df

def get_indices_list_with_capitalization(formatted=True):
    """
    Retourne la liste complète des indices avec leur code et capitalisation
    
    Args:
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        pd.DataFrame: DataFrame avec les colonnes [Indice, Code_Index, Capitalisation (MAD), URL_Complete]
    """
    
    indices_data = get_all_indices_overview(formatted)
    if not indices_data:
        return None
    
    df = format_indices_to_dataframe(indices_data, formatted)
    if df is None or df.empty:
        return None
    
    # Vérifier que la colonne Capitalisation_num existe
    if 'Capitalisation_num' not in df.columns:
        print("❌ Colonne 'Capitalisation_num' non trouvée dans le DataFrame")
        return None
    
    # Sélectionner les colonnes pertinentes
    result_df = df[['Indice', 'Code_Index', 'Capitalisation (MAD)', 'URL_Complete', 'Catégorie', 'Capitalisation_num']].copy()
    
    # Trier par capitalisation (décroissant)
    result_df = result_df.sort_values('Capitalisation_num', ascending=False)
    
    # Supprimer la colonne numérique pour l'affichage final
    result_df = result_df.drop('Capitalisation_num', axis=1)
    
    print(f"✅ Liste de {len(result_df)} indices avec capitalisation récupérée")
    return result_df

def get_main_indices(formatted=True):
    """
    Récupère uniquement les principaux indices (MASI, MASI 20, MASI ESG, MASI Mid and Small Cap)
    
    Args:
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        pd.DataFrame: DataFrame avec les principaux indices
    """
    
    indices_data = get_all_indices_overview(formatted)
    if not indices_data:
        return None
    
    # Filtrer pour ne garder que les principaux indices
    main_indices = []
    for category in indices_data:
        if category.get('title') == 'Principaux indices':
            main_indices = category.get('items', [])
            break
    
    if not main_indices:
        print("❌ Aucun indice principal trouvé")
        return None
    
    # Convertir en DataFrame
    df_main = format_indices_to_dataframe([{'title': 'Principaux indices', 'items': main_indices}], formatted)
    print(f"✅ {len(df_main)} indices principaux récupérés")
    return df_main

def get_sector_indices(formatted=True):
    """
    Récupère uniquement les indices sectoriels
    
    Args:
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        pd.DataFrame: DataFrame avec les indices sectoriels
    """
    
    indices_data = get_all_indices_overview(formatted)
    if not indices_data:
        return None
    
    # Filtrer pour ne garder que les indices sectoriels
    sector_indices = []
    for category in indices_data:
        if category.get('title') == 'Indices sectoriels':
            sector_indices = category.get('items', [])
            break
    
    if not sector_indices:
        print("❌ Aucun indice sectoriel trouvé")
        return None
    
    # Convertir en DataFrame
    df_sector = format_indices_to_dataframe([{'title': 'Indices sectoriels', 'items': sector_indices}], formatted)
    print(f"✅ {len(df_sector)} indices sectoriels récupérés")
    return df_sector

def get_index_by_name(index_name, formatted=True):
    """
    Récupère les données d'un indice spécifique par son nom
    
    Args:
        index_name (str): Nom de l'indice (ex: "MASI", "MASI 20", "MASI BANQUES")
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        dict: Données de l'indice ou None si non trouvé
    """
    
    indices_data = get_all_indices_overview(formatted)
    if not indices_data:
        return None
    
    for category in indices_data:
        for item in category.get('items', []):
            if item.get('index') == index_name:
                # Ajouter le code d'index et l'URL complète
                index_url = item.get('index_url', '')
                item['code_index'] = extract_index_code(index_url)
                item['url_complete'] = f"https://www.casablanca-bourse.com{index_url}" if index_url else ""
                print(f"✅ Indice '{index_name}' trouvé (Code: {item['code_index']})")
                return item
    
    print(f"❌ Indice '{index_name}' non trouvé")
    return None

def get_index_by_code(index_code, formatted=True):
    """
    Récupère les données d'un indice spécifique par son code
    
    Args:
        index_code (str): Code de l'indice (ex: "MASI", "MSI20", "BANK")
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        dict: Données de l'indice ou None si non trouvé
    """
    
    indices_data = get_all_indices_overview(formatted)
    if not indices_data:
        return None
    
    for category in indices_data:
        for item in category.get('items', []):
            current_index_code = extract_index_code(item.get('index_url', ''))
            if current_index_code == index_code:
                # Ajouter le code d'index et l'URL complète
                index_url = item.get('index_url', '')
                item['code_index'] = current_index_code
                item['url_complete'] = f"https://www.casablanca-bourse.com{index_url}" if index_url else ""
                print(f"✅ Indice avec code '{index_code}' trouvé (Nom: {item.get('index')})")
                return item
    
    print(f"❌ Indice avec code '{index_code}' non trouvé")
    return None

def get_top_performers(n=5, period='veille', formatted=True):
    """
    Récupère les indices ayant les meilleures performances
    
    Args:
        n (int): Nombre d'indices à retourner
        period (str): Période de performance ('veille' ou 'annuelle')
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        pd.DataFrame: DataFrame avec les meilleurs performeurs
    """
    
    indices_data = get_all_indices_overview(formatted)
    if not indices_data:
        return None
    
    df = format_indices_to_dataframe(indices_data, formatted)
    if df is None or df.empty:
        return None
    
    # Déterminer la colonne de tri selon la période
    if period == 'annuelle':
        sort_column = 'Variation annuelle (%)'
    else:  # veille par défaut
        sort_column = 'Variation veille (%)'
    
    # Trier par performance (descendant)
    top_performers = df.nlargest(n, sort_column)[['Indice', 'Code_Index', 'Catégorie', sort_column, 'Valeur indice', 'URL_Complete']]
    
    print(f"✅ Top {n} performeurs sur la période {period} récupérés")
    return top_performers

def get_worst_performers(n=5, period='veille', formatted=True):
    """
    Récupère les indices ayant les moins bonnes performances
    
    Args:
        n (int): Nombre d'indices à retourner
        period (str): Période de performance ('veille' ou 'annuelle')
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        pd.DataFrame: DataFrame avec les moins bons performeurs
    """
    
    indices_data = get_all_indices_overview(formatted)
    if not indices_data:
        return None
    
    df = format_indices_to_dataframe(indices_data, formatted)
    if df is None or df.empty:
        return None
    
    # Déterminer la colonne de tri selon la période
    if period == 'annuelle':
        sort_column = 'Variation annuelle (%)'
    else:  # veille par défaut
        sort_column = 'Variation veille (%)'
    
    # Trier par performance (ascendant - les plus petites valeurs)
    worst_performers = df.nsmallest(n, sort_column)[['Indice', 'Code_Index', 'Catégorie', sort_column, 'Valeur indice', 'URL_Complete']]
    
    print(f"✅ {n} moins bons performeurs sur la période {period} récupérés")
    return worst_performers

def export_indices_to_csv(indices_data, filename=None):
    """
    Exporte les données des indices vers un fichier CSV
    
    Args:
        indices_data: Données des indices (DataFrame ou liste de dictionnaires)
        filename (str): Nom du fichier de sortie
    
    Returns:
        str: Chemin du fichier créé ou None en cas d'erreur
    """
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"indices_bourse_casablanca_{timestamp}.csv"
    
    try:
        if isinstance(indices_data, pd.DataFrame):
            df = indices_data
        else:
            df = format_indices_to_dataframe(indices_data)
        
        if df is None or df.empty:
            print("❌ Aucune donnée à exporter")
            return None
        
        # Exclure les colonnes de tri numériques pour l'export
        columns_to_export = [col for col in df.columns if not col.endswith('_num')]
        df_export = df[columns_to_export]
        
        df_export.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"✅ Données exportées vers: {filename}")
        return filename
        
    except Exception as e:
        print(f"❌ Erreur lors de l'export: {e}")
        return None

def get_market_summary(formatted=True):
    """
    Récupère un résumé du marché avec les indicateurs clés
    
    Args:
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        dict: Résumé du marché avec les indicateurs clés
    """
    
    main_indices_df = get_main_indices(formatted)
    if main_indices_df is None or main_indices_df.empty:
        return None
    
    # Vérifier que les colonnes numériques existent
    if 'Capitalisation_num' not in main_indices_df.columns or 'Variation veille (%)' not in main_indices_df.columns:
        print("❌ Colonnes numériques manquantes pour le résumé")
        return None
    
    # Calculer quelques statistiques
    total_capitalization = main_indices_df['Capitalisation_num'].sum()
    avg_daily_variation = main_indices_df['Variation veille (%)'].mean()
    avg_annual_variation = main_indices_df['Variation annuelle (%)'].mean()
    
    # Trouver le meilleur et pire performeur du jour
    best_performer_idx = main_indices_df['Variation veille (%)'].idxmax()
    worst_performer_idx = main_indices_df['Variation veille (%)'].idxmin()
    
    summary = {
        'date_heure': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'nombre_indices_principaux': len(main_indices_df),
        'capitalisation_totale': format_number_french(total_capitalization) if formatted else total_capitalization,
        'capitalisation_totale_num': total_capitalization,
        'variation_moyenne_jour': round(avg_daily_variation, 2),
        'variation_moyenne_annuelle': round(avg_annual_variation, 2),
        'meilleur_performeur': {
            'indice': main_indices_df.loc[best_performer_idx, 'Indice'],
            'code_index': main_indices_df.loc[best_performer_idx, 'Code_Index'],
            'variation': main_indices_df.loc[best_performer_idx, 'Variation veille (%)']
        },
        'pire_performeur': {
            'indice': main_indices_df.loc[worst_performer_idx, 'Indice'],
            'code_index': main_indices_df.loc[worst_performer_idx, 'Code_Index'],
            'variation': main_indices_df.loc[worst_performer_idx, 'Variation veille (%)']
        }
    }
    
    print("✅ Résumé du marché généré avec succès")
    return summary

def get_available_indices_for_composition():
    """
    Retourne la liste des indices disponibles pour récupérer la composition
    avec leur code et capitalisation, triés par capitalisation décroissante
    
    Returns:
        pd.DataFrame: DataFrame avec [Indice, Code_Index, Capitalisation (MAD), URL_Complete]
    """
    
    indices_data = get_all_indices_overview(formatted=True)
    if not indices_data:
        return None
    
    df = format_indices_to_dataframe(indices_data, formatted=True)
    if df is None or df.empty:
        return None
    
    # Vérifier que la colonne Capitalisation_num existe
    if 'Capitalisation_num' not in df.columns:
        print("❌ Colonne 'Capitalisation_num' non trouvée dans le DataFrame")
        # Afficher les colonnes disponibles pour debug
        print(f"Colonnes disponibles: {list(df.columns)}")
        return None
    
    # Filtrer pour ne garder que les indices avec une capitalisation non nulle
    valid_indices = df[df['Capitalisation_num'] > 0].copy()
    
    if valid_indices.empty:
        print("❌ Aucun indice avec capitalisation non nulle trouvé")
        return None
    
    # Trier par capitalisation décroissante (en utilisant la colonne numérique)
    valid_indices = valid_indices.sort_values('Capitalisation_num', ascending=False)
    
    # Sélectionner les colonnes d'intérêt APRÈS le tri
    result_df = valid_indices[['Indice', 'Code_Index', 'Capitalisation (MAD)', 'URL_Complete', 'Catégorie']].copy()
    
    print(f"✅ {len(result_df)} indices disponibles pour composition récupérés")
    return result_df

# # Exemple d'utilisation
# if __name__ == "__main__":
#     # 1. Récupérer tous les indices avec codes et URLs
#     print("=== APERÇU COMPLET DES INDICES AVEC CODES ===")
#     all_indices = get_all_indices_overview(formatted=True)
    
#     if all_indices:
#         df_all = format_indices_to_dataframe(all_indices)
#         print(f"Total d'indices: {len(df_all)}")
#         print(df_all[['Catégorie', 'Indice', 'Code_Index', 'Valeur indice', 'Variation veille (%)']].head(10))
        
#         # Export en CSV
#         export_indices_to_csv(df_all)
    
#     # 2. Liste complète des indices avec capitalisation
#     print("\n=== LISTE COMPLÈTE DES INDICES AVEC CAPITALISATION ===")
#     indices_list = get_indices_list_with_capitalization()
#     if indices_list is not None:
#         print(indices_list.head(10))
    
#     # 3. Indices disponibles pour composition
#     print("\n=== INDICES DISPONIBLES POUR COMPOSITION ===")
#     available_indices = get_available_indices_for_composition()
#     if available_indices is not None:
#         print(available_indices.head(15))
    
#     # 4. Recherche d'un indice par code
#     print("\n=== RECHERCHE INDICE PAR CODE 'MSI20' ===")
#     msi20_index = get_index_by_code("MSI20")
#     if msi20_index:
#         print(f"Nom: {msi20_index.get('index')}")
#         print(f"Valeur: {msi20_index.get('field_index_value')}")
#         print(f"Code: {msi20_index.get('code_index')}")
#         print(f"URL: {msi20_index.get('url_complete')}")
    
#     # 5. Top 5 performeurs du jour avec codes
#     print("\n=== TOP 5 PERFORMERS DU JOUR AVEC CODES ===")
#     top_performers = get_top_performers(n=5, period='veille')
#     if top_performers is not None:
#         print(top_performers)


# 1. get_index_composition : Fonction pour récupérer la composition d'un indice de la Bourse de Casablanca avec buildId dynamique
# 2. get_index_composition_batch : Permet de récupérer la composition de plusieurs indices en lot
# 3. get_composition_for_main_indices : Récupère la composition de tous les indices principaux

def get_index_composition(index_code="MSI20", formatted=True, verify_index=True, build_id=None):
    """
    Récupère la composition d'un indice de la Bourse de Casablanca avec buildId dynamique
    """
    
    # Récupérer le buildId si non fourni
    if build_id is None:
        build_id = get_build_id_cached()
        if not build_id:
            print("❌ Impossible de récupérer le buildId")
            return None
    
    # Vérifier que l'indice existe si demandé
    if verify_index:
        print(f"🔍 Vérification de l'existence de l'indice {index_code}...")
        index_info = get_index_by_code(index_code, formatted=False)
        if not index_info:
            print(f"❌ L'indice {index_code} n'existe pas ou n'est pas disponible")
            return None
        else:
            print(f"✅ Indice {index_code} trouvé: {index_info.get('index')}")
    
    # Headers pour la requête initiale avec buildId dynamique
    headers = {
        'sec-ch-ua-platform': '"Windows"',
        'x-vactory-data-loader': f'/_next/data/{build_id}/fr/live-market/indices/{index_code}.json?slug=live-market&slug=indices&slug={index_code}',
        'Referer': f'https://www.casablanca-bourse.com/fr/live-market/indices/{index_code}',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
    }

    params = {
        'slug': ['live-market', 'indices', index_code],
    }

    try:
        print(f"📊 Récupération de la composition de l'indice {index_code}...")
        
        # Requête initiale pour obtenir les métadonnées avec buildId dynamique
        response = requests.get(
            f'https://www.casablanca-bourse.com/_next/data/{build_id}/fr/live-market/indices/{index_code}.json',
            params=params,
            headers=headers,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Erreur API ({response.status_code}): Impossible d'accéder à la page de l'indice {index_code}")
            return None

        # Le reste du code reste identique...
        data = response.json()
        
        # Extraction de l'ID de l'indice et de tous les IDs de market_watch
        index_id = None
        all_market_watch_ids = []
        
        paragraphs = data['pageProps']['node']['field_vactory_paragraphs']
        
        for block in paragraphs:
            widget_id = block.get('field_vactory_component', {}).get('widget_id', '')
            
            if widget_id == 'bourse_data_listing:index-top':
                raw_json = block['field_vactory_component']['widget_data']
                parsed_data = json.loads(raw_json)
                indice_data = parsed_data['components'][0]['collection']['data']['data'][0]
                self_link = indice_data['links']['self']['href']
                index_id = self_link.split('resourceVersion=id%3A')[-1]
                
            elif widget_id == 'bourse_data_listing:index-composition':
                raw_json = block['field_vactory_component']['widget_data']
                parsed_data = json.loads(raw_json)
                
                filters = parsed_data['components'][0]['collection']['filters']['filter']
                if 'last' in filters and 'condition' in filters['last']:
                    condition = filters['last']['condition']
                    if condition['path'] == 'drupal_internal__id' and condition['operator'] == 'IN':
                        all_market_watch_ids = condition['value']
        
        if not index_id:
            print(f"❌ Impossible de trouver l'ID pour l'indice {index_code}")
            return None
        
        print(f"✅ ID de l'indice {index_code} trouvé: {index_id}")
        
        if not all_market_watch_ids:
            print("❌ Aucun instrument trouvé dans la composition")
            return None
        
        print(f"✅ {len(all_market_watch_ids)} instruments trouvés au total")
        
        # Récupération de toutes les données avec pagination
        all_composition_data = []
        
        # Headers pour les requêtes API paginées
        api_headers = {
            'sec-ch-ua-platform': '"Windows"',
            'Referer': f'https://www.casablanca-bourse.com/fr/live-market/indices/{index_code}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'application/vnd.api+json',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'Content-Type': 'application/vnd.api+json',
            'sec-ch-ua-mobile': '?0',
        }
        
        # DIVISER LES REQUÊTES EN LOTS PLUS PETITS POUR ÉVITER LES ERREURS
        chunk_size = 10  # Réduire la taille des lots pour éviter les URL trop longues
        total_chunks = (len(all_market_watch_ids) + chunk_size - 1) // chunk_size
        
        print(f"📄 Traitement en {total_chunks} lots de {chunk_size} instruments")
        
        for chunk in range(total_chunks):
            start_idx = chunk * chunk_size
            end_idx = min((chunk + 1) * chunk_size, len(all_market_watch_ids))
            chunk_ids = all_market_watch_ids[start_idx:end_idx]
            
            # Construction des paramètres de filtre pour ce lot
            filter_params = []
            for i, market_watch_id in enumerate(chunk_ids):
                filter_params.append((f'filter[last][condition][value][{i}]', market_watch_id))
            
            # Paramètres pour la requête
            params_market_watch = [
                ('fields[instrument]', 'libelleFR,libelleAR,libelleEN,symbol'),
                ('fields[market_watch]', 'bestAskPrice,bestAskSize,bestBidPrice,bestBidSize,capitalisation,closingPrice,coursCourant,cumulTitresEchanges,cumulVolumeEchange,difference,dynamicReferencePrice,highPrice,lowPrice,openingPrice,staticReferencePrice,totalTrades,varVeille,symbol'),
                ('include', 'symbol'),
                ('sort[sort-instrument][path]', 'symbol.libelleFR'),
                ('sort[sort-instrument][direction]', 'ASC'),
                ('page[limit]', str(len(chunk_ids))),
                ('filter[last][condition][path]', 'drupal_internal__id'),
                ('filter[last][condition][operator]', 'IN'),
            ] + filter_params
            
            try:
                print(f"  Traitement du lot {chunk + 1}/{total_chunks} ({len(chunk_ids)} instruments)...")
                
                response_market_watch = requests.get(
                    'https://www.casablanca-bourse.com/api/proxy/fr/api/bourse_data/market_watch',
                    params=params_market_watch,
                    headers=api_headers,
                    verify=False,
                    timeout=30
                )
                
                if response_market_watch.status_code != 200:
                    print(f"❌ Erreur API pour le lot {chunk + 1}: {response_market_watch.status_code}")
                    continue
                
                try:
                    market_data = response_market_watch.json()
                except json.JSONDecodeError as e:
                    print(f"❌ Erreur de parsing JSON pour le lot {chunk + 1}: {e}")
                    continue
                
                if 'data' not in market_data or not market_data['data']:
                    print(f"⚠️ Aucune donnée pour le lot {chunk + 1}")
                    continue
                
                # Traitement des données du lot
                processed_instruments = set()
                instruments_count = 0
                
                for item in market_data['data']:
                    attributes = item.get('attributes', {})
                    symbol_data = None
                    
                    # Recherche des données du symbole dans les relations
                    if 'relationships' in item and 'symbol' in item['relationships']:
                        symbol_id = item['relationships']['symbol']['data']['id']
                        # Rechercher dans les données incluses
                        if 'included' in market_data:
                            for included in market_data['included']:
                                if included['id'] == symbol_id and included['type'] == 'instrument':
                                    symbol_data = included.get('attributes', {})
                                    break
                    
                    # Obtenir l'ID unique de l'instrument
                    instrument_id = None
                    if 'relationships' in item and 'symbol' in item['relationships']:
                        instrument_id = item['relationships']['symbol']['data'].get('meta', {}).get('drupal_internal__target_id')
                    
                    # Éviter les doublons
                    if instrument_id and instrument_id in processed_instruments:
                        continue
                    
                    if instrument_id:
                        processed_instruments.add(instrument_id)
                    
                    # Préparation des données avec gestion des valeurs nulles
                    capitalisation = float(attributes.get('capitalisation', 0) or 0)
                    cours_courant = float(attributes.get('coursCourant', 0) or 0)
                    volume = float(attributes.get('cumulVolumeEchange', 0) or 0)
                    variation = float(attributes.get('varVeille', 0) or 0)
                    difference = float(attributes.get('difference', 0) or 0)
                    high_price = float(attributes.get('highPrice', 0) or 0)
                    low_price = float(attributes.get('lowPrice', 0) or 0)
                    opening_price = float(attributes.get('openingPrice', 0) or 0)
                    
                    row_data = {
                        'instrument_id': instrument_id,
                        'Société': symbol_data.get('libelleFR', '') if symbol_data else '',
                        'Ticker': symbol_data.get('symbol', '') if symbol_data else '',
                        'Dernier cours': format_number_french(cours_courant) if formatted else cours_courant,
                        'Variation (%)': variation,
                        'Différence': difference,
                        'Volume échangé': format_number_french(volume) if formatted else volume,
                        'Capitalisation': format_number_french(capitalisation) if formatted else capitalisation,
                        "Cours d'ouverture": format_number_french(opening_price) if formatted else opening_price,
                        'Plus haut': format_number_french(high_price) if formatted else high_price,
                        'Plus bas': format_number_french(low_price) if formatted else low_price,
                        'Nombre de transactions': int(attributes.get('totalTrades', 0) or 0)
                    }
                    all_composition_data.append(row_data)
                    instruments_count += 1
                
                print(f"  ✅ Lot {chunk + 1}/{total_chunks} traité: {instruments_count} instruments récupérés")
                
                # Pause plus longue pour éviter de surcharger le serveur
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Erreur lors du traitement du lot {chunk + 1}: {e}")
                continue
        
        if all_composition_data:
            df = pd.DataFrame(all_composition_data)
            
            # Supprimer la colonne instrument_id pour le résultat final
            if 'instrument_id' in df.columns:
                df = df.drop('instrument_id', axis=1)
            
            print(f"✅ Composition de l'indice {index_code} récupérée avec succès: {len(df)} instruments uniques")
            return df
        else:
            print(f"❌ Aucune donnée de composition trouvée pour l'indice {index_code}")
            return None
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données de l'indice: {e}")
        return None

def get_index_composition_batch(index_codes, formatted=True):
    """
    Récupère la composition de plusieurs indices en lot
    
    Args:
        index_codes (list): Liste des codes d'indices (ex: ["MSI20", "MASI"])
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        dict: Dictionnaire avec les DataFrames de composition pour chaque indice
    """
    
    results = {}
    
    for index_code in index_codes:
        print(f"\n{'='*50}")
        print(f"Traitement de l'indice: {index_code}")
        print(f"{'='*50}")
        
        composition = get_index_composition(index_code, formatted, verify_index=True)
        if composition is not None:
            results[index_code] = composition
        else:
            print(f"❌ Échec de la récupération pour {index_code}")
        
        # Pause entre les indices pour éviter de surcharger le serveur
        time.sleep(2)
    
    print(f"\n📊 Récapitulatif: {len(results)}/{len(index_codes)} indices traités avec succès")
    return results

def get_composition_for_main_indices(formatted=True):
    """
    Récupère la composition de tous les indices principaux
    
    Args:
        formatted (bool): Si True, formate les nombres avec des espaces pour les milliers
    
    Returns:
        dict: Dictionnaire avec les DataFrames de composition pour chaque indice principal
    """
    
    print("🎯 Récupération de la composition des indices principaux...")
    
    # Récupérer la liste des indices principaux
    main_indices = get_main_indices(formatted=False)
    if main_indices is None or main_indices.empty:
        print("❌ Impossible de récupérer la liste des indices principaux")
        return None
    
    # Extraire les codes des indices principaux
    main_index_codes = main_indices['Code_Index'].tolist()
    
    print(f"📋 Indices principaux à traiter: {', '.join(main_index_codes)}")
    
    # Récupérer la composition en lot
    return get_index_composition_batch(main_index_codes, formatted)


# # 1. Récupération simple avec validation
# print("=== COMPOSITION D'UN INDICE AVEC VALIDATION ===")
# df_msi20 = get_index_composition("MSI20", verify_index=True)
# if df_msi20 is not None:
#     print(df_msi20.head())

# # 2. Test avec un mauvais code d'indice
# print("\n=== TEST AVEC MAUVAIS CODE ===")
# df_invalid = get_index_composition("INVALID_CODE", verify_index=True)

# # 3. Récupération par lots
# print("\n=== RÉCUPÉRATION PAR LOTS ===")
# indices_a_traiter = ["MSI20", "MASI", "BANK"]
# results = get_index_composition_batch(indices_a_traiter)
# for index_code, df in results.items():
#     print(f"{index_code}: {len(df)} instruments") 
#     # Pour le traitement par lot, puisque ça retourne un json il faudra donc si l'on veut récupérer les données individuellement appliquer le code suivant 
#     # # Cas de MSI20
#     # print(results["MSI20"])

#     # # Cas de MASI
#     # print(results["MASI"])

#     # # Cas de BANK
#     # print(results["BANK"])

# # 4. Récupération de tous les indices principaux
# print("\n=== TOUS LES INDICES PRINCIPAUX ===")
# all_main_compositions = get_composition_for_main_indices()
# if all_main_compositions:
#     for index_code, df in all_main_compositions.items():
#         print(f"{index_code}: {len(df)} instruments")
#         # Sauvegarder chaque composition
#         timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"composition_{index_code}_{timestamp}.csv"
#         df.to_csv(filename, index=False, encoding='utf-8-sig')
#         print(f"  📁 Sauvegardé: {filename}")



# Fonction pour récupèrer les données de cotation d'un indice avec buildId dynamique

def get_index_quotation(index_code="MSI20", formatted=True, build_id=None):
    """
    Récupère les données de cotation d'un indice avec buildId dynamique
    """
    
    # Récupérer le buildId si non fourni
    if build_id is None:
        build_id = get_build_id_cached()
        if not build_id:
            print("❌ Impossible de récupérer le buildId")
            return None
    
    # D'abord récupérer l'ID de l'indice avec buildId dynamique
    index_id = None
    try:
        headers = {
            'sec-ch-ua-platform': '"Windows"',
            'x-vactory-data-loader': f'/_next/data/{build_id}/fr/live-market/indices/{index_code}.json?slug=live-market&slug=indices&slug={index_code}',
            'Referer': f'https://www.casablanca-bourse.com/fr/live-market/indices/{index_code}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
        }

        params = {
            'slug': ['live-market', 'indices', index_code],
        }

        response = requests.get(
            f'https://www.casablanca-bourse.com/_next/data/{build_id}/fr/live-market/indices/{index_code}.json',
            params=params,
            headers=headers,
            verify=False,
            timeout=30
        )

        if response.status_code == 200:
            data = response.json()
            paragraphs = data['pageProps']['node']['field_vactory_paragraphs']
            
            for block in paragraphs:
                widget_id = block.get('field_vactory_component', {}).get('widget_id', '')
                if widget_id == 'bourse_data_listing:index-top':
                    raw_json = block['field_vactory_component']['widget_data']
                    parsed_data = json.loads(raw_json)
                    indice_data = parsed_data['components'][0]['collection']['data']['data'][0]
                    self_link = indice_data['links']['self']['href']
                    index_id = self_link.split('resourceVersion=id%3A')[-1]
                    break
    except Exception as e:
        print(f"Erreur lors de la récupération de l'ID de l'indice: {e}")
        return None
    
    # Le reste du code pour récupérer la cotation reste identique...
    if not index_id:
        print(f"❌ Impossible de trouver l'ID pour l'indice {index_code}")
        return None
    
    # Récupération des données de cotation
    try:
        headers_quotation = {
            'sec-ch-ua-platform': '"Windows"',
            'Referer': f'https://www.casablanca-bourse.com/fr/live-market/indices/{index_code}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'application/vnd.api+json',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'Content-Type': 'application/vnd.api+json',
            'sec-ch-ua-mobile': '?0',
        }

        response = requests.get(
            f'https://www.casablanca-bourse.com/api/proxy/fr/api/bourse/dashboard/index_cotation/{index_id}',
            headers=headers_quotation,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"Erreur API cotation: {response.status_code}")
            return None

        data = response.json().get('data', {})
        
        # Préparation des données
        capitalisation = float(data.get('field_market_capitalisation', 0) or 0)
        valeur = float(data.get('field_index_value', 0) or 0)
        plus_bas = float(data.get('field_index_low_value', 0) or 0)
        plus_haut = float(data.get('field_index_high_value', 0) or 0)
        cours_veille = float(data.get('veille', 0) or 0)
        
        quotation_data = [{
            'Indice': index_code,
            'Capitalisation (MAD)': format_number_french(capitalisation) if formatted else capitalisation,
            'Valeur': format_number_french(valeur) if formatted else valeur,
            'Plus bas': format_number_french(plus_bas) if formatted else plus_bas,
            'Plus haut': format_number_french(plus_haut) if formatted else plus_haut,
            'Cours veille': format_number_french(cours_veille) if formatted else cours_veille,
            'Variation annuelle (%)': float(data.get('field_var_year', 0) or 0),
            'Variation veille (%)': float(data.get('field_var_veille', 0) or 0),
            'Diviseur': format_number_french(float(data.get('field_divisor', 0) or 0)) if formatted else float(data.get('field_divisor', 0) or 0)
        }]
        
        df = pd.DataFrame(quotation_data)
        print(f"✅ Cotation de l'indice {index_code} récupérée avec succès")
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de la cotation: {e}")
        return None


# # Exemple
# get_index_quotation("MSI20")



# 1. get_index_id_by_code_simple : Version simplifiée pour récupérer l'ID de l'indice
# 2. get_index_data_by_code : Récupérer les données historiques d'un indice par son code
# 3. get_index_data_by_name : Récupérer Récupère les données historiques d'un indice par son nom

# Fonction pour récupérer l'ID interne d'un indice à partir de son code
def get_index_id_by_code_simple(index_code):
    """
    Version simplifiée pour récupérer l'ID de l'indice
    """
    try:
        build_id = get_build_id_cached()
        if not build_id:
            return None
        
        headers = {
            'sec-ch-ua-platform': '"Windows"',
            'x-vactory-data-loader': f'/_next/data/{build_id}/fr/live-market/indices/{index_code}.json?slug=live-market&slug=indices&slug={index_code}',
            'Referer': f'https://www.casablanca-bourse.com/fr/live-market/indices/{index_code}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
        }

        params = {'slug': ['live-market', 'indices', index_code]}

        print(f"🔧 Récupération de l'ID pour l'indice '{index_code}'...")
        
        response = requests.get(
            f'https://www.casablanca-bourse.com/_next/data/{build_id}/fr/live-market/indices/{index_code}.json',
            params=params,
            headers=headers,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Erreur HTTP: {response.status_code}")
            return None

        data = response.json()
        
        # Convertir tout le JSON en string et chercher avec regex
        json_str = json.dumps(data)
        
        # Pattern principal
        patterns = [
            r'"drupal_internal__tid":\s*"(\d+)"',
            r'"drupal_internal__target_id":\s*"(\d+)"',
            r'"tid":\s*"(\d+)"',
            r'"target_id":\s*"(\d+)"',
            r'indices/(\d+)',  # Pattern alternatif dans les URLs
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, json_str)
            if matches:
                print(f"✅ ID trouvé avec pattern '{pattern}': {matches[0]}")
                return matches[0]
        
        print(f"❌ Aucun ID trouvé pour '{index_code}'")
        print("💡 Debug - Extrait du JSON:")
        print(json_str[:2000])  # Afficher un extrait pour debug
        return None
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return None


# Methode pour récupérer l'ID interne d'un indice à partir de son code en utilisant l'API Next.js
def get_index_id_by_code(index_code):
    """
    Récupère l'ID interne d'un indice à partir de son code en utilisant l'API Next.js
    
    Args:
        index_code (str): Code de l'indice (ex: 'MASIMS')
    
    Returns:
        str: ID interne de l'indice (drupal_internal__tid) ou None si non trouvé
    """
    try:
        # Récupérer le buildId
        build_id = get_build_id_cached()
        if not build_id:
            print(f"❌ Impossible de récupérer le buildId pour l'indice '{index_code}'")
            return None
        
        headers = {
            'sec-ch-ua-platform': '"Windows"',
            'x-vactory-data-loader': f'/_next/data/{build_id}/fr/live-market/indices/{index_code}.json?slug=live-market&slug=indices&slug={index_code}',
            'Referer': f'https://www.casablanca-bourse.com/fr/live-market/indices/{index_code}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
        }

        params = {
            'slug': [
                'live-market',
                'indices',
                index_code,
            ],
        }

        print(f"🔧 Récupération de l'ID pour l'indice '{index_code}'...")
        
        response = requests.get(
            f'https://www.casablanca-bourse.com/_next/data/{build_id}/fr/live-market/indices/{index_code}.json',
            params=params,
            headers=headers,
            verify=False,
            timeout=30
        )

        if response.status_code != 200:
            print(f"❌ Erreur lors de la récupération de l'ID pour '{index_code}': {response.status_code}")
            return None

        data = response.json()
        
        # Méthode 1: Recherche directe dans la structure JSON
        print("🔍 Recherche de l'ID dans la structure JSON...")
        drupal_internal_tid = extract_drupal_tid_from_json(data)
        
        if drupal_internal_tid:
            print(f"✅ ID trouvé pour l'indice '{index_code}': {drupal_internal_tid}")
            return str(drupal_internal_tid)
        
        # Méthode 2: Recherche avec regex dans tout le JSON
        print("🔍 Recherche alternative avec regex...")
        json_str = json.dumps(data)
        pattern = r'"drupal_internal__tid":\s*"(\d+)"'
        matches = re.findall(pattern, json_str)
        
        if matches:
            drupal_internal_tid = matches[0]
            print(f"✅ ID trouvé (méthode regex) pour '{index_code}': {drupal_internal_tid}")
            return str(drupal_internal_tid)
        
        # Méthode 3: Recherche d'autres patterns
        print("🔍 Recherche de patterns alternatifs...")
        alternative_patterns = [
            r'"drupal_internal__target_id":\s*"(\d+)"',
            r'"tid":\s*"(\d+)"',
            r'"target_id":\s*"(\d+)"'
        ]
        
        for pattern in alternative_patterns:
            matches = re.findall(pattern, json_str)
            if matches:
                drupal_internal_tid = matches[0]
                print(f"✅ ID trouvé (pattern alternatif) pour '{index_code}': {drupal_internal_tid}")
                return str(drupal_internal_tid)
                
        print(f"❌ drupal_internal__tid non trouvé pour l'indice '{index_code}'")
        print("💡 Debug: Structure JSON disponible:")
        print(json.dumps(data, indent=2)[:1000] + "...")  # Afficher les premiers 1000 caractères pour debug
        return None
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération de l'ID pour '{index_code}': {e}")
        import traceback
        traceback.print_exc()
        return None

def extract_drupal_tid_from_json(data):
    """
    Extrait le drupal_internal__tid de la structure JSON de différentes manières
    """
    try:
        # Méthode 1: Parcours de la structure connue
        page_props = data.get('pageProps', {})
        node = page_props.get('node', {})
        field_paragraphs = node.get('field_vactory_paragraphs', [])
        
        for paragraph in field_paragraphs:
            component_data = paragraph.get('field_vactory_component', {})
            widget_data = component_data.get('widget_data', '')
            
            if widget_data and isinstance(widget_data, str):
                try:
                    # Parser le JSON stringifié
                    widget_json = json.loads(widget_data)
                    return find_drupal_tid_in_dict(widget_json)
                except json.JSONDecodeError as e:
                    print(f"⚠️ Erreur de parsing JSON dans widget_data: {e}")
                    continue
            elif isinstance(widget_data, dict):
                # Si widget_data est déjà un dict
                return find_drupal_tid_in_dict(widget_data)
        
        # Méthode 2: Recherche récursive dans tout l'objet
        return find_drupal_tid_recursive(data)
        
    except Exception as e:
        print(f"⚠️ Erreur lors de l'extraction structurée: {e}")
        return None

def find_drupal_tid_in_dict(obj):
    """
    Cherche récursivement drupal_internal__tid dans un dictionnaire
    """
    if isinstance(obj, dict):
        # Vérifier si la clé existe directement
        if 'drupal_internal__tid' in obj:
            return obj['drupal_internal__tid']
        
        # Chercher dans les valeurs du dictionnaire
        for key, value in obj.items():
            if key == 'components' and isinstance(value, list):
                for component in value:
                    result = find_drupal_tid_in_dict(component)
                    if result:
                        return result
            elif isinstance(value, (dict, list)):
                result = find_drupal_tid_in_dict(value)
                if result:
                    return result
                    
    elif isinstance(obj, list):
        for item in obj:
            result = find_drupal_tid_in_dict(item)
            if result:
                return result
                
    return None

def find_drupal_tid_recursive(obj, path=""):
    """
    Recherche récursive de drupal_internal__tid dans n'importe quelle structure
    """
    try:
        if isinstance(obj, dict):
            # Vérifier cette niveau
            if 'drupal_internal__tid' in obj:
                print(f"✅ Trouvé à l'emplacement: {path}.drupal_internal__tid")
                return obj['drupal_internal__tid']
            
            # Chercher récursivement
            for key, value in obj.items():
                new_path = f"{path}.{key}" if path else key
                result = find_drupal_tid_recursive(value, new_path)
                if result:
                    return result
                    
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                new_path = f"{path}[{i}]"
                result = find_drupal_tid_recursive(item, new_path)
                if result:
                    return result
                    
    except Exception as e:
        print(f"⚠️ Erreur lors de la recherche récursive à {path}: {e}")
        
    return None

# get_index_id_by_code("MASI")
# get_index_id_by_code("MSI20")
# get_index_id_by_code("MASIMS")


# if __name__ == "__main__":
#     # Tester les nouvelles fonctions
#     test_historical_data_functions()


def get_index_data_by_code(index_code, date, periode='15M', formatted=True):
    """
    Récupère les données historiques d'un indice par son code
    
    Args:
        index_code (str): Code de l'indice (ex: 'MASIMS')
        date (str): Date au format 'YYYY-MM-DD'
        periode (str): Période des données ('15M', '1H', '3H', '1d')
        formatted (bool): Si True, formate les nombres
    
    Returns:
        pd.DataFrame: DataFrame avec les données historiques ou None en cas d'erreur
    """
    try:
        # Récupérer l'ID de l'indice
        index_id = get_index_id_by_code(index_code)
        if not index_id:
            return None
        
        # Convertir la période en intervalle de temps
        if periode == '15M':
            page_limit = 500  # Plus de données pour les périodes courtes
        elif periode == '1H':
            page_limit = 200
        elif periode == '3H':
            page_limit = 100
        elif periode == '1d':
            page_limit = 50
        else:
            page_limit = 250  # Valeur par défaut
        
        headers = {
            'sec-ch-ua-platform': '"Windows"',
            'Referer': f'https://www.casablanca-bourse.com/fr/live-market/indices/{index_code}',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
            'Accept': 'application/vnd.api+json',
            'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
            'Content-Type': 'application/vnd.api+json',
            'sec-ch-ua-mobile': '?0',
        }

        params = {
            'fields[index_watch]': 'drupal_internal__id,transactTime,indexValue',
            'filter[seance][condition][path]': 'transactTime',
            'filter[seance][condition][operator]': 'STARTS_WITH',
            'filter[seance][condition][value]': date,
            'filter[index][condition][path]': 'indexCode.meta.drupal_internal__target_id',
            'filter[index][condition][operator]': '=',
            'filter[index][condition][value]': index_id,
            'filter[ouverture][condition][path]': 'transactTime',
            'filter[ouverture][condition][operator]': '>=',
            'filter[ouverture][condition][value]': f'{date}T09:30:00',
            'page[offset]': '0',
            'page[limit]': str(page_limit),
        }

        print(f"📊 Récupération des données pour {index_code} du {date} (période: {periode})...")
        
        all_data = []
        offset = 0
        
        while True:
            params['page[offset]'] = str(offset)
            
            response = requests.get(
                'https://www.casablanca-bourse.com/api/proxy/fr/api/bourse_data/index_watch',
                params=params,
                headers=headers,
                verify=False,
                timeout=30
            )

            if response.status_code != 200:
                print(f"❌ Erreur API: {response.status_code}")
                break

            data = response.json()
            
            if 'data' not in data or not data['data']:
                break
                
            all_data.extend(data['data'])
            
            # Vérifier s'il y a une page suivante
            if 'links' in data and 'next' in data['links']:
                offset += page_limit
            else:
                break
        
        if not all_data:
            print("❌ Aucune donnée trouvée")
            return None
        
        print(f"✅ {len(all_data)} points de données récupérés")
        
        # Convertir en DataFrame
        df_data = []
        for item in all_data:
            attributes = item.get('attributes', {})
            df_data.append({
                'timestamp': attributes.get('transactTime'),
                'index_value': float(attributes.get('indexValue', 0)),
                'internal_id': attributes.get('drupal_internal__id')
            })
        
        df = pd.DataFrame(df_data)
        
        # Convertir le timestamp en datetime
        df['datetime'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('datetime')
        
        # Agrégation selon la période demandée
        df = aggregate_data_by_period(df, periode)
        
        if formatted:
            df['index_value'] = df['index_value'].apply(lambda x: format_number_french(x) if pd.notna(x) else '0')
        
        return df
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données pour '{index_code}': {e}")
        return None

def get_index_data_by_name(index_name, date, periode='15M', formatted=True):
    """
    Récupère les données historiques d'un indice par son nom
    
    Args:
        index_name (str): Nom de l'indice (ex: 'MASI')
        date (str): Date au format 'YYYY-MM-DD'
        periode (str): Période des données ('15M', '1H', '3H', '1d')
        formatted (bool): Si True, formate les nombres
    
    Returns:
        pd.DataFrame: DataFrame avec les données historiques ou None en cas d'erreur
    """
    try:
        # Récupérer le code de l'indice à partir du nom
        index_data = get_index_by_name(index_name, formatted=False)
        if not index_data:
            print(f"❌ Indice '{index_name}' non trouvé")
            return None
        
        index_code = index_data.get('code_index')
        if not index_code:
            print(f"❌ Code non trouvé pour l'indice '{index_name}'")
            return None
        
        print(f"✅ Code trouvé pour '{index_name}': {index_code}")
        
        # Utiliser la fonction par code
        return get_index_data_by_code(index_code, date, periode, formatted)
        
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des données pour '{index_name}': {e}")
        return None

def aggregate_data_by_period(df, periode):
    """
    Agrège les données selon la période demandée
    
    Args:
        df (pd.DataFrame): DataFrame avec les données brutes
        periode (str): Période d'agrégation ('15M', '1H', '3H', '1d')
    
    Returns:
        pd.DataFrame: DataFrame agrégé
    """
    if df.empty:
        return df
    
    # Définir l'intervalle de rééchantillonnage
    if periode == '15M':
        rule = '15T'  # 15 minutes
    elif periode == '1H':
        rule = '1H'   # 1 heure
    elif periode == '3H':
        rule = '3H'   # 3 heures
    elif periode == '1d':
        rule = '1D'   # 1 jour
    else:
        rule = '15T'  # Par défaut 15 minutes
    
    # Définir le datetime comme index
    df_temp = df.set_index('datetime')
    
    # Rééchantillonner selon la période
    if periode == '1d':
        # Pour les données journalières, prendre la dernière valeur de la journée
        df_resampled = df_temp.resample(rule).last()
    else:
        # Pour les données intraday, prendre la dernière valeur de chaque période
        df_resampled = df_temp.resample(rule).last()
    
    # Supprimer les lignes avec des valeurs manquantes
    df_resampled = df_resampled.dropna()
    
    # Réinitialiser l'index
    df_resampled = df_resampled.reset_index()
    
    # Conserver les colonnes originales
    result_df = df_resampled[['datetime', 'index_value']].copy()
    result_df['timestamp'] = result_df['datetime'].dt.strftime('%Y-%m-%dT%H:%M:%S+00:00')
    
    print(f"✅ Données agrégées en périodes {periode}: {len(result_df)} points")
    return result_df

# # Fonction utilitaire pour tester
# def test_historical_data_functions():
#     """
#     Fonction de test pour les nouvelles fonctions de données historiques
#     """
#     print("=== TEST DES FONCTIONS DE DONNÉES HISTORIQUES ===")
    
#     # Test avec un code d'indice
#     print("\n1. Test avec index_code = 'MSI20'")
#     df_code = get_index_data_by_code('MSI20', '2025-11-07', '1H', formatted=True)
#     if df_code is not None:
#         print(f"Données récupérées: {len(df_code)} lignes")
#         print(df_code.head(10))
    
#     # Test avec un nom d'indice
#     print("\n2. Test avec index_name = 'MASI 20'")
#     df_name = get_index_data_by_name('MASI 20', '2025-11-07', '15M', formatted=True)
#     if df_name is not None:
#         print(f"Données récupérées: {len(df_name)} lignes")
#         print(df_name.head(10))
    
#     # Test avec différentes périodes
#     print("\n3. Test avec différentes périodes pour MASI 20")
#     periods = ['15M', '1H', '3H', '1d']
#     for period in periods:
#         df_period = get_index_data_by_name('MASI 20', '2025-11-07', period, formatted=False)
#         if df_period is not None:
#             print(f"Période {period}: {len(df_period)} points de données")
#             if not df_period.empty:
#                 first_val = df_period['index_value'].iloc[0]
#                 last_val = df_period['index_value'].iloc[-1]
#                 print(f"  Premier: {first_val}, Dernier: {last_val}")





# # Placeholder implementations based on user's original code (trimmed for packaging)
# def get_instrument_details(url_instrument):
#     return {"info": "instrument details placeholder", "url": url_instrument}

# def get_live_market_data(build_id=None, formatted=True):
#     # placeholder: in real use this parses the site's next/data JSON
#     return pd.DataFrame([{"Instrument":"PLACEHOLDER","Dernier cours":None}])

# def get_live_market_data_auto(build_id=None, formatted=True):
#     return get_live_market_data(build_id=build_id, formatted=formatted)

# def get_symbol_id_from_ticker(ticker, build_id=None):
#     # naive placeholder
#     return None

# def get_historical_data(ticker, from_date, to_date, build_id=None):
#     return pd.DataFrame([])

# def get_symbol_id_from_ticker_auto(ticker, build_id=None):
#     return get_symbol_id_from_ticker(ticker, build_id=build_id)

# def get_historical_data_auto(ticker, from_date, to_date, build_id=None):
#     return get_historical_data(ticker, from_date, to_date, build_id=build_id)

# def get_multiple_symbol_ids(tickers, build_id=None):
#     return {t: get_symbol_id_from_ticker(t, build_id=build_id) for t in tickers}

# def get_market_data(marche=59, classes=[50]):
#     return pd.DataFrame([])

# def get_top_gainers(limit=10):
#     return pd.DataFrame([])

# def get_top_losers(limit=10):
#     return pd.DataFrame([])

# def get_most_active(limit=10, by='volume'):
#     return pd.DataFrame([])

# def get_sector_performance():
#     return pd.DataFrame([])

# def get_market_summary():
#     return {}

# def get_technical_indicators(ticker):
#     return {}

# def export_market_data(format='csv', filename=None):
#     return None

# def get_volume_overview(build_id=None):
#     return None, None, None, None, None

# def get_volume_data(from_date, to_date, formatted=True):
#     return pd.DataFrame([])

# def get_capitalization_data(from_date, to_date):
#     return pd.DataFrame([])

# def get_capitalization_overview(formatted=True, build_id=None):
#     return {"global_cap": pd.DataFrame(), "top_10": pd.DataFrame(), "sectorial": pd.DataFrame()}

# # indices placeholders
# def get_all_indices_overview(formatted=True):
#     return []

# def extract_index_code(index_url):
#     return index_url.strip('/').split('/')[-1].upper()

# def format_indices_to_dataframe(indices_data, formatted=True):
#     return pd.DataFrame(indices_data)

# def get_indices_list_with_capitalization(formatted=True):
#     return pd.DataFrame([])

# def get_main_indices(formatted=True):
#     return pd.DataFrame([])

# def get_sector_indices(formatted=True):
#     return pd.DataFrame([])

# def get_index_by_name(index_name, formatted=True):
#     return None

# def get_index_by_code(index_code, formatted=True):
#     return None

# def get_top_performers(n=5, period='veille', formatted=True):
#     return pd.DataFrame([])

# def get_worst_performers(n=5, period='veille', formatted=True):
#     return pd.DataFrame([])

# def export_indices_to_csv(indices_data, filename=None):
#     return None

# def get_available_indices_for_composition():
#     return pd.DataFrame([])

# def get_index_composition(index_code="MSI20", formatted=True, verify_index=True, build_id=None):
#     return pd.DataFrame([])

# def get_index_composition_batch(index_codes, formatted=True):
#     return {c: get_index_composition(c, formatted=formatted) for c in index_codes}

# def get_composition_for_main_indices(formatted=True):
#     return {}

# def get_index_quotation(index_code="MSI20", formatted=True, build_id=None):
#     return {}

# def get_index_id_by_code(index_code):
#     return None

# def extract_drupal_tid_from_json(data):
#     return None

# def find_drupal_tid_in_dict(obj):
#     return None

# def find_drupal_tid_recursive(obj, path=""):
#     return None

# def get_index_id_by_code_simple(index_code):
#     return None

# def get_index_data_by_code(index_code, date=None, periode='15M', formatted=True):
#     return pd.DataFrame([])

# def get_index_data_by_name(index_name, date=None, periode='15M', formatted=True):
#     return pd.DataFrame([])

# def aggregate_data_by_period(df, periode):
#     return df
