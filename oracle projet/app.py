# =========================================================================
# MODULE: Administration Oracle et Intelligence Artificielle
# FILE: app.py (Serveur Backend Flask - VS Code)
# ROLE: Liaison réelle entre la base Oracle et l'Interface Web (Dashboard)
# =========================================================================

from flask import Flask, jsonify, request
from flask_cors import CORS
import oracledb
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
# Activation du CORS pour autoriser l'interface HTML (dashboard.html) à appeler cette API
CORS(app)

# Configuration de la connexion Oracle (À modifier selon vos paramètres)
ORACLE_USER = "SYSTEM"
ORACLE_PASSWORD = "Iliass123456789*"  # Remplacez par votre vrai mot de passe SYSTEM
ORACLE_DSN = "localhost:1521/XE"       # Remplacez par votre SID (ex: ORCL ou XE)

def get_oracle_connection():
    return oracledb.connect(user=ORACLE_USER, password=ORACLE_PASSWORD, dsn=ORACLE_DSN)

@app.route('/api/predict', methods=['GET'])
def predict_tablespace():
    connection = None
    try:
        # 1. Connexion et extraction des données d'historique
        connection = get_oracle_connection()
        cursor = connection.cursor()
        
        query = """
            SELECT id_mesure, used_space_mb, max_space_mb, pct_used 
            FROM ts_space_history 
            WHERE tablespace_name = 'TS_ADMIN_IA'
            ORDER BY id_mesure ASC
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({"error": "Aucune donnée trouvée dans Oracle. Lancez d'abord oracle_setup.sql."}), 404
        
        # 2. Structurer la Data dans un DataFrame Pandas
        df = pd.DataFrame(rows, columns=['id', 'used_space_mb', 'max_space_mb', 'pct_used'])
        
        # 3. Entraînement du modèle de régression linéaire
        X = df[['id']].values  # Variables explicatives (les Jours/Mesures)
        y = df['used_space_mb'].values  # Variable à prédire (Espace occupé)
        
        model = LinearRegression()
        model.fit(X, y)
        
        m = float(model.coef_[0])
        b = float(model.intercept_)
        
        # Calcul du coefficient de détermination R²
        r2 = float(model.score(X, y))
        
        # 4. Prédiction de l'échéance (Time-To-Failure)
        # Seuil de saturation (Dernière capacité maximale enregistrée)
        max_capacity = float(df['max_space_mb'].iloc[-1])
        
        # Résolution de l'équation : max_capacity = m * X + b => X = (max_capacity - b) / m
        if m > 0:
            jour_saturation = (max_capacity - b) / m
        else:
            jour_saturation = 999.0  # Stable si croissance nulle ou négative
            
        # Préparation des données pour le graphique
        history_labels = [f"Jour {int(r[0])}" for r in rows]
        history_values = [float(r[1]) for r in rows]
        
        # Ajouter 5 jours de projection future dans le graphique
        all_labels = list(history_labels)
        regression_values = []
        
        # Calculer la droite ajustée pour l'historique
        for i in range(1, len(rows) + 1):
            regression_values.append(round(m * i + b, 2))
            
        # Calculer les projections futures
        last_day = len(rows)
        for i in range(last_day + 1, last_day + 6):
            all_labels.append(f"Jour {i}")
            regression_values.append(round(m * i + b, 2))
            
        return jsonify({
            "status": "success",
            "connection_mode": "REAL_ORACLE",
            "current_capacity": max_capacity,
            "last_measure": float(df['used_space_mb'].iloc[-1]),
            "slope": round(m, 2),
            "r2": round(r2, 4),
            "ttf_day": round(jour_saturation, 2),
            "labels": all_labels,
            "history_data": history_values + [None]*5, # None pour ne pas dessiner l'historique sur la projection
            "regression_data": regression_values
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if connection:
            connection.close()

@app.route('/api/remediate', methods=['POST'])
def remediate_tablespace():
    connection = None
    try:
        # Exécution de la commande d'administration autonome (Resize du tablespace)
        connection = get_oracle_connection()
        cursor = connection.cursor()
        
        # Commande DBA réelle pour augmenter la taille du fichier de données à 100MB
        # (Attention: adaptez le chemin physique de votre fichier dbf si nécessaire)
        query = "ALTER DATABASE DATAFILE 'ts_admin_ia.dbf' RESIZE 100M"
        cursor.execute(query)
        connection.commit()
        
        # Mettre à jour l'historique pour notifier la nouvelle taille maximale
        update_query = "UPDATE ts_space_history SET max_space_mb = 100.00 WHERE tablespace_name = 'TS_ADMIN_IA'"
        cursor.execute(update_query)
        connection.commit()
        
        return jsonify({
            "status": "success",
            "message": "Ordre d'administration autonome exécuté : ALTER DATABASE DATAFILE ... RESIZE 100M"
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    print("==========================================================")
    print(" SERVEUR DE MAINTENANCE PRÉDICTIVE ORACLE IA DEMARRÉ      ")
    print(" Adresse locale : http://127.0.0.1:5000                   ")
    print("==========================================================")
    app.run(port=5000, debug=True)