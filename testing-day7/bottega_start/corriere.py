"""
SIMULATORE del servizio esterno del corriere "SpediVeloce S.p.A.".

Fate finta che questo processo giri su un server di un'altra azienda:
NON è codice nostro e NON va modificato.
Avvio:  python corriere.py   ->  http://localhost:8001

Variabili d'ambiente per simulare un fornitore "inaffidabile" (le useremo più avanti):
    CORRIERE_LATENZA=3      ogni risposta arriva dopo 3 secondi
    CORRIERE_ERRORI=0.3     il 30% delle richieste risponde 503
"""

import os
import random
import time

from flask import Flask, request, jsonify

app = Flask(__name__)

LATENZA = float(os.getenv("CORRIERE_LATENZA", "0"))
PROBABILITA_ERRORE = float(os.getenv("CORRIERE_ERRORI", "0"))


@app.get("/tariffa")
def tariffa():
    if LATENZA:
        time.sleep(LATENZA)
    if random.random() < PROBABILITA_ERRORE:
        return jsonify({"errore": "servizio temporaneamente non disponibile"}), 503

    cap = request.args.get("cap", "")
    try:
        peso = float(request.args.get("peso", ""))
    except ValueError:
        return jsonify({"errore": "peso non valido"}), 400

    if len(cap) != 5 or not cap.isdigit():
        return jsonify({"errore": "cap non valido"}), 400
    if peso <= 0:
        return jsonify({"errore": "peso non valido"}), 400

    costo = 4.90 if peso <= 2 else 9.90
    return jsonify({"costo": costo})


if __name__ == "__main__":
    print(f"[SpediVeloce] latenza={LATENZA}s errori={PROBABILITA_ERRORE * 100:.0f}%")
    app.run(port=8001)
