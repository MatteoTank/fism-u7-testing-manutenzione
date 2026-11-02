"""
Il primo test di sistema: il server è vivo?
Prerequisito: python app.py acceso in un altro terminale.
"""

import requests

BASE_URL = "http://localhost:8000"


def test_health_risponde_ok():
    # Act
    risposta = requests.get(f"{BASE_URL}/api/health", timeout=5)

    # Assert
    assert risposta.status_code == 200
    assert risposta.json()["status"] == "ok"
