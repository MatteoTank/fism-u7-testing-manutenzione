"""
La Bottega - backend dell'e-commerce aziendale.

Ereditato dal team precedente. "Funziona", dicono.
Avvio:  python app.py   ->  http://localhost:8000
"""

import json
import os
import secrets

from flask import Flask, request, jsonify, send_from_directory

import preventivo
import spedizioni

app = Flask(__name__, static_folder="static")

AMBIENTE = os.getenv("BOTTEGA_ENV", "sviluppo")

# --- "Database" in memoria (si azzera a ogni riavvio) -----------------------

PRODOTTI_INIZIALI = [
    {"id": 1, "nome": "Tastiera meccanica", "prezzo": 89.90, "stock": 5, "peso": 1.2, "immagine": "/static/img/tastiera.svg"},
    {"id": 2, "nome": "Mouse ergonomico", "prezzo": 34.50, "stock": 10, "peso": 0.3, "immagine": "/static/img/mouse.svg"},
    {"id": 3, "nome": "Monitor 27 pollici", "prezzo": 249.00, "stock": 2, "peso": 6.5, "immagine": "/static/img/monitor.svg"},
    {"id": 4, "nome": "Cavo USB-C", "prezzo": 9.99, "stock": 50, "peso": 0.1, "immagine": "/static/img/cavo.svg"},
]

UTENTI = {
    "mario": {"password": "password123", "tipo": "nuovo"},
    "giulia": {"password": "vip2026", "tipo": "vip"},
}

prodotti = {}
carrelli = {}   # username -> {prodotto_id: quantita}
token_attivi = {}   # token -> username
ordini = []


def reset_dati():
    prodotti.clear()
    for p in PRODOTTI_INIZIALI:
        prodotti[p["id"]] = dict(p)
    carrelli.clear()
    token_attivi.clear()
    ordini.clear()


reset_dati()


# --- Helper -----------------------------------------------------------------

def utente_autenticato():
    intestazione = request.headers.get("Authorization", "")
    if not intestazione.startswith("Bearer "):
        return None
    token = intestazione.removeprefix("Bearer ")
    return token_attivi.get(token)


# --- Frontend ---------------------------------------------------------------

@app.get("/")
def home():
    return send_from_directory(app.static_folder, "index.html")


# --- API --------------------------------------------------------------------

@app.get("/api/health")
def health():
    return jsonify({"status": "ok", "ambiente": AMBIENTE})


@app.get("/api/prodotti")
def lista_prodotti():
    return jsonify(list(prodotti.values()))


@app.get("/api/prodotti/<int:prodotto_id>")
def dettaglio_prodotto(prodotto_id):
    prodotto = prodotti.get(prodotto_id)
    if prodotto is None:
        return jsonify({"errore": "prodotto non trovato"}), 404
    return jsonify(prodotto)


@app.post("/api/login")
def login():
    dati = json.loads(request.get_data())
    username = dati["username"]
    password = dati["password"]

    if username not in UTENTI:
        return jsonify({"errore": "utente inesistente"}), 401
    if UTENTI[username]["password"] != password:
        return jsonify({"errore": "password errata"}), 401

    token = secrets.token_hex(16)
    token_attivi[token] = username
    return jsonify({"token": token, "tipo": UTENTI[username]["tipo"]})


@app.get("/api/carrello")
def leggi_carrello():
    username = utente_autenticato()
    if username is None:
        return jsonify({"errore": "autenticazione richiesta"}), 401

    righe = []
    for prodotto_id, quantita in carrelli.get(username, {}).items():
        prodotto = prodotti[prodotto_id]
        righe.append({
            "prodotto_id": prodotto_id,
            "nome": prodotto["nome"],
            "prezzo": prodotto["prezzo"],
            "quantita": quantita,
            "subtotale": round(prodotto["prezzo"] * quantita, 2),
        })
    totale = round(sum(r["subtotale"] for r in righe), 2)
    return jsonify({"righe": righe, "totale": totale})


@app.post("/api/carrello")
def aggiungi_al_carrello():
    username = utente_autenticato()
    if username is None:
        return jsonify({"errore": "autenticazione richiesta"}), 401

    dati = json.loads(request.get_data())
    prodotto_id = dati["prodotto_id"]
    quantita = dati["quantita"]

    prodotto = prodotti.get(prodotto_id)
    if prodotto is None:
        return jsonify({"errore": "prodotto non trovato"}), 404
    if quantita > prodotto["stock"]:
        return jsonify({"errore": "quantità non disponibile"}), 409

    carrello = carrelli.setdefault(username, {})
    carrello[prodotto_id] = carrello.get(prodotto_id, 0) + quantita
    return jsonify({"prodotto_id": prodotto_id, "quantita": carrello[prodotto_id]}), 201


@app.post("/api/ordini")
def checkout():
    username = utente_autenticato()
    if username is None:
        return jsonify({"errore": "autenticazione richiesta"}), 401

    dati = json.loads(request.get_data())
    cap = dati["cap"]
    codice_sconto = dati.get("codice_sconto", "")

    carrello = carrelli.get(username, {})
    if not carrello:
        return jsonify({"errore": "carrello vuoto"}), 400

    righe = []
    peso_totale = 0
    for prodotto_id, quantita in carrello.items():
        prodotto = prodotti[prodotto_id]
        righe.append({"prezzo": prodotto["prezzo"], "quantita": quantita})
        peso_totale += prodotto["peso"] * quantita

    costo_spedizione = spedizioni.costo_spedizione(cap, peso_totale)
    totale = preventivo.calcola_totale(righe, UTENTI[username]["tipo"], codice_sconto, cap, costo_spedizione)

    for prodotto_id, quantita in carrello.items():
        prodotti[prodotto_id]["stock"] -= quantita
    carrelli[username] = {}

    ordine = {"id": len(ordini) + 1, "utente": username, "totale": totale}
    ordini.append(ordine)
    return jsonify(ordine), 201


@app.post("/api/reset")
def reset():
    """Riporta i dati allo stato iniziale. Esiste SOLO per i test automatici."""
    if AMBIENTE == "produzione":
        return jsonify({"errore": "non disponibile in produzione"}), 403
    reset_dati()
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    app.run(port=8000, debug=True)
