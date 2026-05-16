from flask import Flask, request, jsonify
import requests
import psycopg2
import os

app = Flask(__name__)

# 🔹 URLs externas
URL_ALERTAS = "https://externoformiddle--GuillermoHerna8.replit.app/procesar"
URL_MANTENIMIENTO = "https://externoformiddle--GuillermoHerna8.replit.app/mantenimiento"

# 🔹 Conexión a Neon
DATABASE_URL = os.environ["DATABASE_URL"]

def guardar_en_db(data):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO sensores (sensor, zona, presion, caudal, alerta, mantenimiento)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data["sensor"],
            data["zona"],
            data["presion"],
            data["caudal"],
            data["alerta"],
            data["mantenimiento"]
        ))

        conn.commit()
        cursor.close()
        conn.close()

        print("💾 Guardado en Neon")

    except Exception as e:
        print("🔥 ERROR DB:", e)


@app.route('/')
def home():
    return "Middleware con PostgreSQL (Neon) 🚀"


@app.route('/orquestar', methods=['POST'])
def orquestar():
    data = request.json

    datos_transformados = {
        "sensorId": data["id_sensor"],
        "location": data["zona"],
        "pressure": data["presion_kpa"],
        "flow": data["caudal_lps"],
        "status": data["estado"]
    }

    try:
        # 🔹 API alertas
        resp_alerta = requests.post(URL_ALERTAS, json=datos_transformados).json()

        resultado = {
            "sensor": datos_transformados["sensorId"],
            "alerta": resp_alerta.get("resultado", "Sin respuesta")
        }

        # 🔹 decisión
        if datos_transformados["pressure"] < 150:
            resp_mant = requests.post(URL_MANTENIMIENTO, json=datos_transformados).json()
            resultado["mantenimiento"] = resp_mant.get("accion", "Sin acción")
        else:
            resultado["mantenimiento"] = "No requerido"

        # 🔥 guardar en Neon
        guardar_en_db({
            "sensor": resultado["sensor"],
            "zona": datos_transformados["location"],
            "presion": datos_transformados["pressure"],
            "caudal": datos_transformados["flow"],
            "alerta": resultado["alerta"],
            "mantenimiento": resultado["mantenimiento"]
        })

        return jsonify(resultado)

    except Exception as e:
        print("🔥 ERROR:", e)
        return jsonify({"error": str(e)})
