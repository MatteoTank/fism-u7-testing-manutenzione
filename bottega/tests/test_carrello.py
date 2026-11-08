import pytest
import requests

""" --------------- Livello 1 ------------------- """
@pytest.mark.parametrize("header", [
    {},
    {"Authorization": "Bearer fnsaj43nio443hwejnfniusnaf"},
    {"Authorization": "afnjkndf53453mèoiif4"}
])
def test_carrello_no_auth(header, base_url):
    response = requests.get(f"{base_url}/api/carrello", headers=header, timeout=5)
    assert response.status_code == 401

def test_aggiunta_carrello(base_url, auth):
    risposta = requests.post(
        f"{base_url}/api/carrello",
        json={"prodotto_id": 2, "quantita": 2},
        headers=auth,
        timeout=5
    )

    assert risposta.status_code == 201

""" --------------- Livello 2 ------------------- """

def test_controllo_aggiunta_carrello(base_url, auth):
    requests.post(
        f"{base_url}/api/carrello",
        json={"prodotto_id": 1, "quantita": 1},
        headers=auth,
        timeout=5
    )

    carrello = requests.get(
        f"{base_url}/api/carrello",
        headers=auth,
        timeout=5
    ).json()

    assert len(carrello['righe']) == 1
    assert carrello['righe'][0]['quantita'] == 1
    assert carrello['totale'] == 89.90

# Sad path del carrello
@pytest.mark.parametrize("body, atteso",[
    ({"prodotto_id": 2, "quantita": -3}, 400),
    ({"prodotto_id": 2, "quantita": 0}, 400),
    ({"prodotto_id": 2, "quantita": "2"}, 400),
    ({"prodotto_id": 2}, 400),
    ({"prodotto_id": 999, "quantita": 1}, 404),
    ({"prodotto_id": 3, "quantita": 99}, 409)
])
def test_sad_path_carrello(body, atteso, base_url, auth):
    risposta = requests.post(
        f"{base_url}/api/carrello",
        json=body,
        headers=auth,
        timeout=5
    )

    assert risposta.status_code == atteso

@pytest.mark.parametrize("body",[
    {"username":"Gennaro", "password":"password123"},
    {"username":"Mario", "password":"password"}
])
def test_sicurezza(body, base_url):
    risposta = requests.post(
        f"{base_url}/api/login",
        json=body,
        timeout=5
    )

    assert risposta.status_code == 401
    assert risposta.json()['errore'] == "credenziali non valide"

""" --------------- Livello 3 ------------------- """

def test_flusso_completo(base_url, auth):
    prodotto = requests.get(f"{base_url}/api/prodotti/1", timeout=5)
    stock = prodotto.json()['stock']

    risposta = requests.post(
        f"{base_url}/api/carrello",
        json={"prodotto_id": 1, "quantita": 2},
        headers=auth,
        timeout=5
    )

    checkout = requests.post(
        f"{base_url}/api/ordini",
        json={"cap": "50100"},
        headers=auth,
        timeout=5
    )

    carrello = requests.get(
        f"{base_url}/api/carrello",
        headers=auth,
        timeout=5
    )

    prodottoAfter = requests.get(f"{base_url}/api/prodotti/1", timeout=5)

    assert checkout.status_code == 201
    assert checkout.json()['totale'] == 179.80
    assert len(carrello.json()['righe']) == 0
    assert stock - prodottoAfter.json()['stock'] == 2

def test_ladro(base_url, auth):
    prodotto = requests.get(f"{base_url}/api/prodotti/2", timeout=5)
    stock = prodotto.json()['stock']

    risposta1 = requests.post(
        f"{base_url}/api/carrello",
        json={"prodotto_id": 2, "quantita": -3},
        headers=auth,
        timeout=5
    )

    risposta2 = requests.post(
        f"{base_url}/api/carrello",
        json={"prodotto_id": 1, "quantita": 1},
        headers=auth,
        timeout=5
    )

    checkout = requests.post(
        f"{base_url}/api/ordini",
        json={"cap": "50100"},
        headers=auth,
        timeout=5
    )

    carrello = requests.get(
        f"{base_url}/api/carrello",
        headers=auth,
        timeout=5
    )

    prodottoAfter = requests.get(f"{base_url}/api/prodotti/2", timeout=5)

    assert checkout.status_code == 201
    #assert checkout.json()['totale'] == 179.80
    assert len(carrello.json()['righe']) == 0
    assert stock - prodottoAfter.json()['stock'] == 7