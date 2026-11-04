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
