"""
conftest.py dei test E2E.

FILE DI PARTENZA del lab di oggi pomeriggio: copiatelo in bottega/tests/e2e/conftest.py
(la cartella tests/e2e/ la create voi).

Due responsabilità, entrambe "Arrange scritto una volta sola" (G1):
1. il SISTEMA acceso: se la Bottega non risponde, la fixture accende corriere e app con subprocess
   (proprio il subprocess del semestre 1) e li spegne a fine sessione;
2. lo STATO pulito: prima di ogni test, POST /api/reset.

pytest-playwright fornisce già le fixture `page`, `context`, `browser`.
Qui ridefiniamo `base_url`: pytest-playwright la usa per risolvere page.goto("/").
"""

import os
import subprocess
import sys
import time
from pathlib import Path

import pytest
import requests

RADICE_BOTTEGA = Path(__file__).resolve().parents[2]   # tests/e2e/conftest.py -> bottega/
URL_BOTTEGA = os.getenv("BOTTEGA_URL", "http://localhost:8000")
URL_CORRIERE = os.getenv("CORRIERE_URL", "http://localhost:8001")


def _risponde(url: str) -> bool:
    try:
        requests.get(url, timeout=1)
        return True
    except requests.ConnectionError:
        return False


def _attendi_avvio(url: str, processo: subprocess.Popen, log: Path, secondi: float = 15) -> None:
    """Attende che il server risponda. Niente sleep(3) "a sentimento": si interroga finché è pronto."""
    scadenza = time.monotonic() + secondi
    while time.monotonic() < scadenza:
        if processo.poll() is not None:
            pytest.exit(f"Il server è morto all'avvio (exit code {processo.returncode}). Log: {log}")
        if _risponde(url):
            return
        time.sleep(0.2)   # questo è polling di un PROCESSO, non attesa nel browser: qui è lecito
    pytest.exit(f"Il server non risponde dopo {secondi}s: {url}. Log: {log}")


@pytest.fixture(scope="session")
def server_bottega(tmp_path_factory):
    """Garantisce che corriere e Bottega siano accesi per tutta la sessione.

    - Se la Bottega risponde già (l'avete accesa voi in due terminali): la RIUSA e non la spegne.
    - Altrimenti la accende, con BOTTEGA_ENV=test (niente debugger/reloader), e la spegne alla fine.
    """
    if _risponde(f"{URL_BOTTEGA}/api/health"):
        yield URL_BOTTEGA
        return

    cartella_log = tmp_path_factory.mktemp("server")
    ambiente = {**os.environ, "BOTTEGA_ENV": "test"}
    processi = []
    try:
        for script, url_pronto in [
            ("corriere.py", f"{URL_CORRIERE}/tariffa?cap=50100&peso=1"),
            ("app.py", f"{URL_BOTTEGA}/api/health"),
        ]:
            log = cartella_log / f"{script}.log"
            # stdout su FILE, mai subprocess.PIPE: una pipe che nessuno legge si riempie e blocca il server
            with open(log, "w") as file_log:
                processo = subprocess.Popen(
                    [sys.executable, script],
                    cwd=RADICE_BOTTEGA,
                    env=ambiente,
                    stdout=file_log,
                    stderr=subprocess.STDOUT,
                )
            processi.append(processo)
            _attendi_avvio(url_pronto, processo, log)
        yield URL_BOTTEGA
    finally:
        for processo in reversed(processi):
            processo.terminate()
            try:
                processo.wait(timeout=5)
            except subprocess.TimeoutExpired:
                processo.kill()


@pytest.fixture(scope="session")
def base_url(server_bottega):
    """pytest-playwright usa questa fixture: page.goto("/") diventa http://localhost:8000/."""
    return server_bottega


@pytest.fixture(autouse=True)
def stato_pulito(base_url):
    """La stessa fixture di stamattina (Lab 2 di martedì): prima di OGNI test il server torna pulito.
    Domanda: perché serve ancora, se ogni test ha già un browser nuovo e pulito?"""
    requests.post(f"{base_url}/api/reset", timeout=5)


@pytest.fixture
def context(context):
    """Le AZIONI (click, fill...) aspettano al massimo 5 secondi invece di 30, come gli expect().
    Un test E2E che fallisce deve fallire in fretta: in CI ogni secondo d'attesa si paga."""
    context.set_default_timeout(5_000)
    return context
