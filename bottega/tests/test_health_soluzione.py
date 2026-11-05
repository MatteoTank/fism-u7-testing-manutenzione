"""
SOLUZIONE TEST
Il primo test di sistema: il server è vivo?
Prerequisito: python app.py acceso in un altro terminale.
"""

import pytest
import requests
from jsonschema import validate, ValidationError

BASE_URL = "http://localhost:8000"


def test_health_risponde_ok():
    # Act
    risposta = requests.get(f"{BASE_URL}/api/health", timeout=5)

    # Assert
    assert risposta.status_code == 200
    assert risposta.json()["status"] == "ok"

def test_lista_prodotti_non_vuota():
    #Act 
    risposta = requests.get(f"{BASE_URL}/api/prodotti", timeout=5)

    #Assert
    assert risposta.status_code == 200
    assert risposta.headers['Content-Type'] == 'application/json'
    prodotti = risposta.json()
    assert len(prodotti) > 0

def test_prodotto_1():
    #Act
    risposta = requests.get(f"{BASE_URL}/api/prodotti/1", timeout=5)

    #Assert
    assert risposta.status_code == 200
    prodotto = risposta.json()
    assert prodotto['id'] == 1

# --------------------- Livello 2 --------------------------------------------



#Act
response = requests.get(f"{BASE_URL}/api/prodotti", timeout=5)
prodotti = response.json()

@pytest.mark.parametrize("prodotto", prodotti)
def test_validazione_schema(prodotto):
    SCHEMA_PRODOTTO = {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "nome": {"type": "string"},
            "prezzo": {"type": "number"},
            "stock": {"type": "integer"},
            "peso": {"type": "number"},
            "immagine": {"type": "string", "format":"uri"},
        },
        "required": ["id", "nome", "prezzo", "stock", "peso", "immagine"],
        "additionalProperties": False,
    }

    try:
        validate(prodotto, SCHEMA_PRODOTTO)
    except ValidationError as e:
        pytest.fail(f"Validazione fallita per il prodotto con ID {prodotto.get('id')}: {e.message}")

@pytest.mark.parametrize("prodottoId", [999, 0, -1, "abc"])
def test_prodotto_inesistente(prodottoId):
    risposta = requests.get(f"{BASE_URL}/api/prodotti/{prodottoId}")

    assert risposta.status_code == 404

# --------------------- Livello 3 --------------------------------------------
    

@pytest.mark.parametrize("body, code", [
    ('{"username": "mario"', 400),
    ("non sono json",400),
    ("",400),
    ('{"username": "mario"}',400),
    ('{"password": "password123"}',400),
    ("[]",400)
])
def test_request_body_failure(body, code):
    response = requests.post(f"{BASE_URL}/api/login", data=body, headers={"Content-Type": "application/json"}, timeout=5)
    assert response.status_code == code
    assert "errore" in response.json()
