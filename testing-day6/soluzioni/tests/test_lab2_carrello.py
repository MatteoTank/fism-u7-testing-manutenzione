"""
LAB 2 — Soluzione del LIVELLO 1 (il resto del lab lo facciamo venerdì).

Nota: test_aggiunta_al_carrello passa la prima volta. Rilanciate pytest una seconda volta
e guardate cosa succede: è il punto di partenza del Livello 2.
"""

import pytest
import requests


def test_login_corretto_restituisce_token(base_url):
    risposta = requests.post(
        f"{base_url}/api/login",
        json={"username": "mario", "password": "password123"},
        timeout=5,
    )

    assert risposta.status_code == 200
    assert len(risposta.json()["token"]) > 0


@pytest.mark.parametrize(
    "headers",
    [
        {},  # nessun header
        {"Authorization": "Bearer token-inventato"},  # token falso
        {"Authorization": "token-senza-bearer"},  # formato sbagliato
    ],
)
def test_carrello_senza_autenticazione_401(base_url, headers):
    risposta = requests.get(f"{base_url}/api/carrello", headers=headers, timeout=5)

    assert risposta.status_code == 401


def test_aggiunta_al_carrello(base_url, auth):
    risposta = requests.post(
        f"{base_url}/api/carrello",
        json={"prodotto_id": 2, "quantita": 2},
        headers=auth,
        timeout=5,
    )

    assert risposta.status_code == 201
    assert risposta.json() == {"prodotto_id": 2, "quantita": 2}


# =============================================================================
# Livello 2: Ingegneria
# =============================================================================


# --- 1. Non fidarti della risposta: rileggi lo stato -------------------------
def test_aggiunta_visibile_leggendo_il_carrello(base_url, auth):
    # Arrange: aggiungo 2 mouse (34.50 l'uno)
    requests.post(
        f"{base_url}/api/carrello",
        json={"prodotto_id": 2, "quantita": 2},
        headers=auth,
        timeout=5,
    )

    # Act: rileggo il carrello con un'ALTRA chiamata
    carrello = requests.get(f"{base_url}/api/carrello", headers=auth, timeout=5).json()

    # Assert
    assert len(carrello["righe"]) == 1
    assert carrello["righe"][0]["quantita"] == 2
    assert carrello["totale"] == 69.00


# --- 2. L'isolamento: è la fixture stato_pulito in conftest.py ---------------


# --- 3. Sad path del carrello: UN solo test parametrizzato -------------------
@pytest.mark.parametrize(
    "body, status_atteso",
    [
        ({"prodotto_id": 2, "quantita": -3}, 400),  # quantità negativa
        ({"prodotto_id": 2, "quantita": 0}, 400),  # quantità zero
        ({"prodotto_id": 2, "quantita": "2"}, 400),  # tipo sbagliato
        ({"prodotto_id": 2}, 400),  # campo mancante
        ({"prodotto_id": 999, "quantita": 1}, 404),  # prodotto inesistente
        ({"prodotto_id": 3, "quantita": 99}, 409),  # oltre lo stock
    ],
)
def test_aggiunta_al_carrello_sad_paths(base_url, auth, body, status_atteso):
    risposta = requests.post(
        f"{base_url}/api/carrello", json=body, headers=auth, timeout=5
    )

    assert risposta.status_code == status_atteso


# --- 4. Sicurezza: il login non rivela se l'utente esiste --------------------
@pytest.mark.parametrize(
    "username, password",
    [
        ("utente_che_non_esiste", "qualcosa"),  # utente inesistente
        ("mario", "password_sbagliata"),  # utente vero, password sbagliata
    ],
)
def test_login_fallito_non_rivela_se_utente_esiste(base_url, username, password):
    risposta = requests.post(
        f"{base_url}/api/login",
        json={"username": username, "password": password},
        timeout=5,
    )

    assert risposta.status_code == 401
    assert risposta.json()["errore"] == "credenziali non valide"
