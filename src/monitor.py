import requests
import pandas as pd
import yaml
import os
from sqlalchemy.orm import sessionmaker

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
            print(f"Fetching IoCs from {source['url']} with headers {source['headers']}")
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

# Fonction pour envoyer une notification par email



def send_email(alert):
    sender_email = "your_email@example.com"
    receiver_email = "recipient@example.com"
    password = os.getenv("EMAIL_PASSWORD")

    message = MIMEMultipart("alternative")
    message["Subject"] = "IoC Alert"
    message["From"] = sender_email
    message["To"] = receiver_email

    text = f"Alert: Malicious IoC detected - {alert}"
    part = MIMEText(text, "plain")
    message.attach(part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

def send_slack_alert(alert):
    client = WebClient(token=os.getenv("SLACK_TOKEN"))

    try:
        response = client.chat_postMessage(
            channel="#your-channel",
            text=f"Alert: Malicious IoC detected - {alert}"
        )
    except SlackApiError as e:
        print(f"Error sending Slack message: {e.response['error']}")

# Fonction pour envoyer une notification Slack
def send_slack_alert(alert):
    client = WebClient(token="your-slack-bot-token")

    try:
        response = client.chat_postMessage(
            channel="#your-channel",
            text=f"Alert: Malicious IoC detected - {alert}"
        )
    except SlackApiError as e:
        print(f"Error sending Slack message: {e.response['error']}")

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

# Exemple de fonction d'alerte
def alert(ioc):
    alert_message = f"Alert: Malicious IoC detected - {ioc}"
    send_email(alert_message)
    send_slack_alert(alert_message)
    return alert_message

if __name__ == "__main__":
    config = load_config()
    monitor_system(config)
