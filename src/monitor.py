import requests
import pandas as pd
import yaml
import os

# Lire le fichier de configuration
def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Fonction pour récupérer les IoC depuis une source externe ou utiliser des données de test
def fetch_iocs(ioc_sources=None, test_data=None):
    if test_data is not None:
        return pd.DataFrame(test_data)
    
    iocs_list = []
    for source in ioc_sources:
        try:
            response = requests.get(source['url'], headers=source['headers'])
            response.raise_for_status()
            iocs = response.json()
            if 'data' in iocs:
                iocs_list.append(pd.DataFrame(iocs['data']))
            else:
                iocs_list.append(pd.DataFrame(iocs))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching IoCs from {source['url']}: {e}")
    
    if iocs_list:
        return pd.concat(iocs_list, ignore_index=True)
    else:
        return pd.DataFrame()

# Fonction pour surveiller les systèmes locaux
def monitor_system(config):
    iocs = fetch_iocs(ioc_sources=config['ioc_sources'])
    print("IoCs fetched:", iocs)

    # Logique de détection de base
    for index, ioc in iocs.iterrows():
        if check_local_system(ioc):
            alert(ioc)

# Exemple de fonction pour vérifier les systèmes locaux
def check_local_system(ioc):
    # Implémentez la logique pour vérifier les IoC sur vos systèmes locaux
    if ioc['ipAddress'] in get_local_logs():
        return True
    return False

# Fonction simulée pour récupérer des logs locaux
def get_local_logs():
    return ["192.168.1.1", "192.168.1.2"]

# Exemple de fonction d'alerte
def alert(ioc):
    print(f"Alert: Malicious IoC detected - {ioc}")

if __name__ == "__main__":
    config = load_config()
    monitor_system(config)
