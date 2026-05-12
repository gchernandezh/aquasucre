from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# 🔹 URLs de tus APIs (las de Replit)
URL_ALERTAS = "https://externoformiddle--GuillermoHerna8.replit.app/procesar"
URL_MANTENIMIENTO = "https://externoformiddle--GuillermoHerna8.replit.app/mantenimiento"

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

    # 🔹 Llamar sistema de alertas
    resp_alerta = requests.post(URL_ALERTAS, json=datos_transformados).json()

    resultado = {
        "sensor": datos_transformados["sensorId"],
        "alerta": resp_alerta["resultado"]
    }

    # 🔹 Decisión
    if datos_transformados["pressure"] < 150:
        resp_mant = requests.post(URL_MANTENIMIENTO, json=datos_transformados).json()
        resultado["mantenimiento"] = resp_mant["accion"]
    else:
        resultado["mantenimiento"] = "No requerido"

    return jsonify(resultado)

# 🔹 Ruta base (para prueba)
@app.route('/')
def home():
    return "Middleware AquaSucre funcionando"