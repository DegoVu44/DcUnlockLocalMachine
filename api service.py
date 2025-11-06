import requests
import time
import os
from flask import Flask, jsonify

# ---------------- CONFIG ----------------
USERNAME = "diegopinelli7@gmail.com"
API_KEY = "20Z-PRO-FBN-8PC-FO6-EMQ-R16-LOG"
API_ENDPOINT = "https://activeunlocker.com/api/index.php"
PING_INTERVAL = 120  # segundos entre reintentos de registro
# ---------------------------------------

app = Flask(__name__)

def get_public_ip():
    try:
        ip = requests.get("https://api.ipify.org").text
        print(f"[*] IP pública detectada: {ip}")
        return ip
    except Exception as e:
        print(f"[!] No se pudo obtener IP pública: {e}")
        return None

def register_ip():
    """
    Intentar registrar la IP haciendo la primera petición a ActiveUnlocker.
    Retorna True si la API acepta la IP.
    """
    payload = {
        "action": "getimeiServices",
        "username": USERNAME,
        "accesskey": API_KEY
    }

    try:
        r = requests.post(API_ENDPOINT, json=payload, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if "ERROR" in data:
                print(f"⚠️ Error devuelto por la API: {data['ERROR']}")
                return False
            print("[+] API aceptó la IP y devolvió datos de servicios.")
            print(data)
            return True
        else:
            print(f"[!] HTTP {r.status_code} al intentar registrar IP")
            return False
    except Exception as e:
        print(f"[!] Error en request a API: {e}")
        return False

def auto_register_loop():
    """
    Loop para reintentar registro de IP cada PING_INTERVAL segundos hasta que funcione
    """
    while True:
        if register_ip():
            print("[✅] IP registrada correctamente. Servicios listos.")
            break
        print(f"[i] Reintentando en {PING_INTERVAL} segundos...")
        time.sleep(PING_INTERVAL)

# ------------------- Flask -------------------
@app.route("/", methods=["GET"])
def home():
    return "Servicio Render ActiveUnlocker listo. Ver logs para estado de IP.", 200

# ------------------- MAIN --------------------
if __name__ == "__main__":
    # Ejecuta el loop en un hilo separado para Render
    import threading
    t = threading.Thread(target=auto_register_loop, daemon=True)
    t.start()

    port = int(os.environ.get("PORT", 10000))  # Render asigna el puerto vía variable
    app.run(host="0.0.0.0", port=port)
