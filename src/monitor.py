import requests
import pandas as pd
import yaml
import os

# Lire le fichier de configuration
def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Fonction pour récupérer les IoC depuis une source externe
def fetch_iocs(ioc_sources=None, test_data=None):
    if test_data is not None:
        return pd.DataFrame(test_data)

    iocs_list = []
    for source in ioc_sources:
        try:
            response = requests.get(source)
            response.raise_for_status()
            iocs = response.json()
            iocs_list.append(pd.DataFrame(iocs))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching IoCs from {source}: {e}")
    
    if iocs_list:
        return pd.concat(iocs_list, ignore_index=True)
    else:
        return pd.DataFrame()

# Fonction pour surveiller les systèmes locaux
def monitor_system(config):
    iocs = fetch_iocs(ioc_sources=config['ioc_sources'])
    print("IoCs fetched:", iocs)

    # Logique basique pour vérifier les IoC
    for index, ioc in iocs.iterrows():
        # Exemple : Vérifiez si une adresse IP malveillante est présente dans les logs locaux
        if check_local_system(ioc):
            alert(ioc)

# Exemple de fonction pour vérifier les systèmes locaux
def check_local_system(ioc):
    # Implémentez la logique pour vérifier les IoC sur vos systèmes locaux
    # Par exemple, vérifier les logs pour les adresses IP
    return False

# Exemple de fonction d'alerte
def alert(ioc):
    print(f"Alert: Malicious IoC detected - {ioc}")

if __name__ == "__main__":
    config = load_config()
    monitor_system(config)
