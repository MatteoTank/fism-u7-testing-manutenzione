import pytest
import requests

@pytest.mark.chaos
def test_checkout_corriere_guasto(base_url, auth):
    # Arrange: Aggiunta al carrello 
    requests.post(
        f"{base_url}/api/carrello",
        json={"prodotto_id": 2, "quantita": 2},
        headers=auth,
        timeout=5
    )

    # Act: Checkout
    risposta = requests.post(
        f"{base_url}/api/ordini",
        json={"cap": "50100"},
        headers=auth,
        timeout=15
    )

    

    # Asserts
    assert risposta.status_code == 503
    assert risposta.json() == {"errore": "servizio spedizioni non disponibile"}
    assert risposta.elapsed.total_seconds() < 8

    carrello = requests.get(
        f"{base_url}/api/carrello",
        headers=auth,
        timeout=5
    ).json()
    assert len(carrello["righe"]) == 1