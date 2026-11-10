"""
conftest.py — il "magazzino" delle fixture (Lab 2, Livelli 1 e 2).
pytest lo carica da solo: le fixture definite qui sono disponibili
in ogni file di test della cartella, senza bisogno di import.
"""

import pytest
import requests


# scope="session": l'indirizzo non cambia, basta calcolarlo una volta.
# Serve anche quando installerete Playwright: porta con sé un plugin che ha
# già una fixture base_url "di sessione", e con lo scope di default pytest
# si lamenterebbe (ScopeMismatch).
@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8000"


# --- Livello 2: isolamento ---------------------------------------------------
# Il server ha memoria: il carrello di un test "sporca" il test dopo.
# autouse=True: pytest la esegue prima di OGNI test, anche se nessuno la chiede.
# Gira prima di token/auth: il reset cancella anche i token, poi la fixture
# token fa un login nuovo.
@pytest.fixture(autouse=True)
def stato_pulito(base_url):
    requests.post(f"{base_url}/api/reset", timeout=5)


@pytest.fixture
def token(base_url):
    """Fa il login come 'mario' e restituisce il token."""
    risposta = requests.post(
        f"{base_url}/api/login",
        json={"username": "mario", "password": "password123"},
        timeout=5,
    )
    return risposta.json()["token"]


@pytest.fixture
def auth(token):
    """Header di autenticazione pronto all'uso."""
    return {"Authorization": f"Bearer {token}"}
