from flask import Flask, render_template, redirect, url_for, request
import requests
import pandas as pd
import yaml
import os
import matplotlib.pyplot as plt
import io
import base64
from sqlalchemy.orm import sessionmaker
from src.database import engine, Alert

app = Flask(__name__)

# Lire le fichier de configuration
def load_config(config_path='config/config.yaml'):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Route pour afficher les alertes
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Nombre d'alertes par page
    Session = sessionmaker(bind=engine)
    session = Session()
    alerts = session.query(Alert).filter(Alert.detected_at.is_(None)).paginate(page, per_page, False)
    next_url = url_for('index', page=alerts.next_num) if alerts.has_next else None
    prev_url = url_for('index', page=alerts.prev_num) if alerts.has_prev else None
    return render_template('index.html', alerts=alerts.items, next_url=next_url, prev_url=prev_url)

# Route pour marquer une alerte comme traitée
@app.route('/resolve/<int:alert_id>')
def resolve_alert(alert_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    alert = session.query(Alert).get(alert_id)
    alert.detected_at = datetime.datetime.utcnow()
    session.commit()
    return redirect(url_for('index'))

# Route pour afficher les alertes traitées
@app.route('/resolved')
def resolved_alerts():
    Session = sessionmaker(bind=engine)
    session = Session()
    alerts = session.query(Alert).filter(Alert.detected_at.isnot(None)).all()
    return render_template('resolved.html', alerts=alerts)

@app.route('/stats')
def stats():
    Session = sessionmaker(bind=engine)
    session = Session()
    alerts = session.query(Alert).all()

    # Créer un graphique des alertes par pays
    country_counts = pd.DataFrame([a.country_code for a in alerts], columns=['country_code']).value_counts()
    plt.figure(figsize=(10, 5))
    country_counts.plot(kind='bar')
    plt.title('Alerts by Country')
    plt.xlabel('Country')
    plt.ylabel('Count')

    img = io.BytesIO()
    plt.savefig(img, format='png')
    img.seek(0)
    plot_url = base64.b64encode(img.getvalue()).decode()

    return render_template('stats.html', plot_url=plot_url)

if __name__ == '__main__':
    app.run(debug=True)
