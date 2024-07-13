import requests
import pandas as pd
import yaml
import os
from sqlalchemy.orm import sessionmaker
import time

if __name__ == "__main__" and __package__ is None:
    import sys
    from os import path
    sys.path.append(path.abspath(path.join(path.dirname(__file__), '..')))
    from src.database import engine, Alert
else:
    from .database import engine, Alert

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from twilio.rest import Client
import logging
from dotenv import load_dotenv

# Charger les variables d'environnement à partir du fichier .env
load_dotenv()

# Lire le fichier de configuration
def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Fonction pour récupérer les IoC depuis une source externe ou utiliser des données de test
def fetch_iocs(ioc_sources=None, test_data=None, retries=5, initial_wait_time=60, cache_file='cache/iocs_cache.csv'):
    if test_data is not None:
        return pd.DataFrame(test_data)
    
    iocs_list = []
    for source in ioc_sources:
        attempt = 0
        wait_time = initial_wait_time
        while attempt < retries:
            try:
                print(f"Fetching IoCs from {source['url']} with headers {source['headers']}")
                response = requests.get(source['url'], headers=source['headers'])
                response.raise_for_status()
                iocs = response.json()
                if 'data' in iocs:
                    iocs_list.append(pd.DataFrame(iocs['data']))
                else:
                    iocs_list.append(pd.DataFrame(iocs))
                break  # Exit the loop if request is successful
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    print(f"Rate limit exceeded. Waiting for {wait_time} seconds before retrying...")
                    time.sleep(wait_time)
                    attempt += 1
                    wait_time *= 2  # Exponential backoff
                else:
                    print(f"Error fetching IoCs from {source['url']}: {e}")
                    break
            except requests.exceptions.RequestException as e:
                print(f"Error fetching IoCs from {source['url']}: {e}")
                break
        
        if attempt == retries:
            print("Max retries reached. Attempting to use cached data if available.")
            if os.path.exists(cache_file):
                print(f"Loading IoCs from cache file {cache_file}.")
                return pd.read_csv(cache_file)
            else:
                print("No cache file found. Returning empty DataFrame.")
                return pd.DataFrame()
    
    if iocs_list:
        combined_iocs = pd.concat(iocs_list, ignore_index=True)
        combined_iocs.to_csv(cache_file, index=False)
        return combined_iocs
    else:
        return pd.DataFrame()

# Fonction pour envoyer une notification par SMS
def send_sms_alert(alert):
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        print("Twilio credentials not found.")
        return

    try:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"Alert: Malicious IoC detected - {alert}",
            from_='+ID_TWILIO_PHONE_NUMBER',  
            to='+12345678901'
        )
        print(f"SMS sent: {message.sid}")
    except Exception as e:
        print(f"Failed to send SMS: {e}")

# Configurer la journalisation
logging.basicConfig(filename='activity.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Exemple de fonction d'alerte mise à jour
def alert(ioc):
    alert_message = f"Alert: Malicious IoC detected - {ioc}"
    logging.info(alert_message)
    # send_email(alert_message)
    # send_slack_alert(alert_message)
    send_sms_alert(alert_message)
    return alert_message

# Fonction pour surveiller les systèmes locaux
def monitor_system(config):
    Session = sessionmaker(bind=engine)
    session = Session()
    iocs = fetch_iocs(ioc_sources=config['ioc_sources'])
    print("IoCs fetched:", iocs)

    # Logique de détection avancée
    alerts = []
    for index, ioc in iocs.iterrows():
        if check_local_system(ioc):
            alert_msg = alert(ioc)
            alerts.append(alert_msg)
            # Ajouter l'alerte à la base de données
            new_alert = Alert(
                ip_address=ioc['ipAddress'],
                country_code=ioc['countryCode'],
                abuse_confidence_score=ioc['abuseConfidenceScore'],
                last_reported_at=pd.to_datetime(ioc['lastReportedAt'])
            )
            session.add(new_alert)
            session.commit()
    if alerts:
        for alert_msg in alerts:
            print(alert_msg)
    else:
        print("No threats detected.")

# Exemple de fonction pour vérifier les systèmes locaux
def check_local_system(ioc):
    # Implémentez la logique pour vérifier les IoC sur vos systèmes locaux
    # Par exemple, vérifier les logs pour les adresses IP
    if ioc['ipAddress'] in get_local_logs():
        return True
    return False

# Fonction simulée pour récupérer des logs locaux
def get_local_logs():
    # Ajoutez une adresse IP malveillante pour tester
    return ["192.168.1.1", "117.50.137.84"]

if __name__ == "__main__":
    config = load_config()
    monitor_system(config)
