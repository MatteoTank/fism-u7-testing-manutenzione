"""
LAB 1 — Soluzione: il contratto pubblico (endpoint senza autenticazione).
"""

import pytest
import requests
from jsonschema import validate

SCHEMA_PRODOTTO = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "nome": {"type": "string", "minLength": 1},
        "prezzo": {"type": "number", "exclusiveMinimum": 0},
        "stock": {"type": "integer", "minimum": 0},
        "peso": {"type": "number", "exclusiveMinimum": 0},
        "immagine": {"type": "string"},
    },
    "required": ["id", "nome", "prezzo", "stock", "peso", "immagine"],
    "additionalProperties": False,
}


# --- Livello 1: Sopravvivenza ------------------------------------------------

def test_health(base_url):
    risposta = requests.get(f"{base_url}/api/health", timeout=5)

    assert risposta.status_code == 200
    assert risposta.json()["status"] == "ok"


def test_lista_prodotti_non_vuota(base_url):
    risposta = requests.get(f"{base_url}/api/prodotti", timeout=5)

    assert risposta.status_code == 200
    assert risposta.headers["Content-Type"] == "application/json"
    assert len(risposta.json()) > 0


def test_dettaglio_prodotto_esistente(base_url):
    risposta = requests.get(f"{base_url}/api/prodotti/1", timeout=5)

    assert risposta.status_code == 200
    assert risposta.json()["id"] == 1


# --- Livello 2: Ingegneria ---------------------------------------------------

def test_ogni_prodotto_rispetta_lo_schema(base_url):
    prodotti = requests.get(f"{base_url}/api/prodotti", timeout=5).json()

    for prodotto in prodotti:
        validate(instance=prodotto, schema=SCHEMA_PRODOTTO)


@pytest.mark.parametrize("id_inesistente", ["999", "0", "-1", "abc"])
def test_prodotto_inesistente_404_in_json(base_url, id_inesistente):
    risposta = requests.get(f"{base_url}/api/prodotti/{id_inesistente}", timeout=5)

    assert risposta.status_code == 404
    # Regola generale n.1 del contratto: anche gli errori sono JSON
    assert risposta.headers["Content-Type"] == "application/json"
    assert "errore" in risposta.json()


# --- Livello 3: Escalation — payload corrotti sul login ----------------------

@pytest.mark.parametrize("body", [
    '{"username": "mario"',            # JSON troncato
    "non sono json",                   # testo libero
    "",                                # body vuoto
    '{"username": "mario"}',           # manca password
    '{"password": "password123"}',     # manca username
    "[]",                              # JSON valido ma del tipo sbagliato
])
def test_login_payload_corrotto_400(base_url, body):
    risposta = requests.post(
        f"{base_url}/api/login",
        data=body,
        headers={"Content-Type": "application/json"},
        timeout=5,
    )

    assert risposta.status_code == 400
    assert "errore" in risposta.json()
