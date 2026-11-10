"""
Client del servizio esterno del corriere (SpediVeloce S.p.A.).
Il servizio NON è nostro: non possiamo modificarlo, possiamo solo chiamarlo.
"""

import os

import requests

CORRIERE_URL = os.getenv("CORRIERE_URL", "http://localhost:8001")

class ServizioSpedizioniNonDisponibile(Exception):
    pass

def costo_spedizione(cap: str, peso: float) -> float:
    try:
        risposta = requests.get(f"{CORRIERE_URL}/tariffa", params={"cap": cap, "peso": peso}, timeout=3)

        risposta.raise_for_status()
    except requests.RequestException as errore:
        raise ServizioSpedizioniNonDisponibile(str(errore)) from errore    
    return risposta.json()["costo"]
