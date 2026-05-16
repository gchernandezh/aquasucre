from flask import Flask, request, jsonify
import requests
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
from datetime import datetime

app = Flask(__name__)

# 🔹 URLs de APIs externas (Replit)
URL_ALERTAS = "https://externoformiddle--GuillermoHerna8.replit.app/procesar"
URL_MANTENIMIENTO = "https://externoformiddle--GuillermoHerna8.replit.app/mantenimiento"

# 🔹 Inicializar Firebase
cred_dict = json.loads(os.environ["FIREBASE_KEY"])
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)

db = firestore.client()

@app.route('/')
def home():
    return "Middleware funcionando con Firebase 🚀"

@app.route('/orquestar', methods=['POST'])
def orquestar():
    data = request.json

    # 🔹 Transformación
    datos_transformados = {
        "sensorId": data["id_sensor"],
        "location": data["zona"],
        "pressure": data["presion_kpa"],
        "flow": data["caudal_lps"],
        "status": data["estado"]
    }

    try:
        # 🔹 Llamar API de alertas
        resp_alerta = requests.post(URL_ALERTAS, json=datos_transformados).json()

        resultado = {
            "sensor": datos_transformados["sensorId"],
            "alerta": resp_alerta.get("resultado", "Sin respuesta")
        }

        # 🔹 Decisión
        if datos_transformados["pressure"] < 150:
            resp_mant = requests.post(URL_MANTENIMIENTO, json=datos_transformados).json()
            resultado["mantenimiento"] = resp_mant.get("accion", "Sin acción")
        else:
            resultado["mantenimiento"] = "No requerido"

        # 🔥 GUARDAR EN FIREBASE
        print("📦 Intentando guardar en Firebase...")
        db.collection("sensores").add({
            "sensor": datos_transformados["sensorId"],
            "zona": datos_transformados["location"],
            "presion": datos_transformados["pressure"],
            "caudal": datos_transformados["flow"],
            "alerta": resultado["alerta"],
            "mantenimiento": resultado["mantenimiento"],
            "timestamp": datetime.now().isoformat()
        })

        return jsonify(resultado)

    except Exception as e:
        print("🔥 ERROR EN FIREBASE:", e)
        return jsonify({"error": str(e)})
