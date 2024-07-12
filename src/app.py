from flask import Flask, render_template
import requests
import pandas as pd
import yaml
import os
from sqlalchemy.orm import sessionmaker
from src.database import engine, Alert  # Chemin absolu utilisé ici

app = Flask(__name__)

# Lire le fichier de configuration
def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Fonction pour récupérer les IoC depuis une source externe
def fetch_iocs(ioc_sources=None):
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

# Exemple de fonction pour vérifier les systèmes locaux
def check_local_system(ioc):
    # Implémentez la logique pour vérifier les IoC sur vos systèmes locaux
    # Par exemple, vérifier les logs pour les adresses IP
    if ioc['ipAddress'] in get_local_logs():
        return True
    return False

# Fonction simulée pour récupérer des logs locaux
def get_local_logs():
    # Cette fonction doit récupérer et renvoyer les logs de votre système
    return ["192.168.1.1", "192.168.1.2"]

# Exemple de fonction d'alerte
def alert(ioc):
    return f"Alert: Malicious IoC detected - {ioc}"

# Route pour afficher les alertes
@app.route('/')
def index():
    Session = sessionmaker(bind=engine)
    session = Session()
    alerts = session.query(Alert).all()
    return render_template('index.html', alerts=alerts)

if __name__ == '__main__':
    app.run(debug=True)
