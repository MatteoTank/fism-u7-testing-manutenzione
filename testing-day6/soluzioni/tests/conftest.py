"""
conftest.py — il "magazzino" delle fixture (Livello 1 del Lab 2).
pytest lo carica da solo: le fixture definite qui sono disponibili
in ogni file di test della cartella, senza bisogno di import.
"""

import pytest
import requests


@pytest.fixture
def base_url():
    return "http://localhost:8000"


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
