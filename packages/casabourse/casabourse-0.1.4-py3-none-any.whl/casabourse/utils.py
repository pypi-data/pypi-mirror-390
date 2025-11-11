# utils.py - utilities for casabourse
import requests, json, time, re, pandas as pd
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Variable globale pour le cache du buildId
_BUILD_ID_CACHE = {
    'build_id': None,
    'timestamp': 0,
    'cache_duration': 3600  # 1 heure en secondes
}

def get_build_id():
    """
    Récupère dynamiquement le buildId depuis la page d'accueil de la Bourse de Casablanca
    
    Returns:
        str: Le buildId actuel ou None en cas d'erreur
    """
    headers = {
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Chromium";v="142", "Google Chrome";v="142", "Not_A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }

    try:
        # print("🔧 Récupération du buildId depuis la page d'accueil...")
        response = requests.get('https://www.casablanca-bourse.com/fr', headers=headers, verify=False, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Erreur lors de l'accès à la page d'accueil: {response.status_code}")
            return None
        
        # Recherche du script contenant les données JSON
        match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', response.text)
        
        if not match:
            print("❌ Script __NEXT_DATA__ non trouvé dans la page")
            return None
        
        # Parser le JSON
        next_data = json.loads(match.group(1))
        build_id = next_data.get('buildId')
        
        if build_id:
            # print(f"✅ BuildId récupéré avec succès: {build_id}")
            return build_id
        else:
            print("❌ BuildId non trouvé dans les données JSON")
            return None
            
    except Exception as e:
        print(f"❌ Erreur lors de la récupération du buildId: {e}")
        return None

def get_build_id_cached(force_refresh=False):
    """
    Récupère le buildId avec cache pour éviter de le récupérer à chaque appel
    
    Args:
        force_refresh (bool): Force la récupération même si le cache est valide
    
    Returns:
        str: Le buildId actuel
    """
    global _BUILD_ID_CACHE
    
    current_time = time.time()
    
    # Vérifier si le cache est encore valide
    if (not force_refresh and 
        _BUILD_ID_CACHE['build_id'] and 
        (current_time - _BUILD_ID_CACHE['timestamp']) < _BUILD_ID_CACHE['cache_duration']):
        # print(f"✅ Utilisation du buildId en cache: {_BUILD_ID_CACHE['build_id']}")
        return _BUILD_ID_CACHE['build_id']
    
    # Récupérer un nouveau buildId
    new_build_id = get_build_id()
    if new_build_id:
        _BUILD_ID_CACHE['build_id'] = new_build_id
        _BUILD_ID_CACHE['timestamp'] = current_time
        return new_build_id
    else:
        # Si échec de récupération, utiliser le cache même expiré
        if _BUILD_ID_CACHE['build_id']:
            print(f"⚠️ Utilisation du buildId cache expiré: {_BUILD_ID_CACHE['build_id']}")
            return _BUILD_ID_CACHE['build_id']
        else:
            print("❌ Aucun buildId disponible")
            return None

def format_number_french(number):
    """
    Formate un nombre avec des espaces pour les milliers et une virgule pour les décimales
    Format français : 48 364 865,45
    """
    if pd.isna(number) or number == 0:
        return "0"
    
    try:
        # Convertir en float puis en int pour la partie entière
        number_float = float(number)
        integer_part = int(number_float)
        decimal_part = round(number_float - integer_part, 2)
        
        # Formater la partie entière avec des espaces
        formatted_integer = f"{integer_part:,}".replace(",", " ")
        
        # Ajouter la partie décimale si nécessaire
        if decimal_part > 0:
            decimal_str = f"{decimal_part:.2f}".split('.')[1]
            return f"{formatted_integer},{decimal_str}"
        else:
            return formatted_integer
    except (ValueError, TypeError):
        return str(number)

def with_build_id(func):
    """
    Décorateur pour injecter automatiquement le buildId dans les fonctions
    """
    def wrapper(*args, **kwargs):
        if 'build_id' not in kwargs or kwargs['build_id'] is None:
            kwargs['build_id'] = get_build_id_cached()
        return func(*args, **kwargs)
    return wrapper

def format_mad(value):
    """
    Formate une valeur numérique en chaîne avec des espaces entre les milliers
    et deux décimales, selon le style financier marocain.

    Exemple : 48247364.52 → "48 247 364.52"

    Parameters:
        value (float or str): Valeur à formater.

    Returns:
        str: Valeur formatée ou valeur brute si non convertible.
    """
    try:
        return f"{float(value):,.2f}".replace(",", " ").replace(".00", ".00")
    except:
        return value