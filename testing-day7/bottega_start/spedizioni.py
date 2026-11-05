"""
Client del servizio esterno del corriere (SpediVeloce S.p.A.).
Il servizio NON è nostro: non possiamo modificarlo, possiamo solo chiamarlo.
"""

import os

import requests

CORRIERE_URL = os.getenv("CORRIERE_URL", "http://localhost:8001")


def costo_spedizione(cap: str, peso: float) -> float:
    risposta = requests.get(f"{CORRIERE_URL}/tariffa", params={"cap": cap, "peso": peso})
    return risposta.json()["costo"]
