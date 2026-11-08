# SETUP — Giorno 7: il browser che si comanda da solo

> 📖 Una parola non vi è chiara? Cercatela in [`CONCETTI_BASE.md`](../CONCETTI_BASE.md), il dizionario del corso.

> ⏰ **Stamattina si riparte dai lab di martedì**, con **corriere e app accesi** come martedì (punto 3 qui sotto):
> - prima il **Livello 2 del Lab 2** ([`testing-day6/lab2_autenticazione/README.md`](../testing-day6/lab2_autenticazione/README.md)): stato verificato con una seconda chiamata, isolamento dei test, sad path del carrello;
> - poi il **Lab 3** ([`testing-day6/lab3_dipendenze_esterne/README.md`](../testing-day6/lab3_dipendenze_esterne/README.md)): il corriere, il mock, il timeout.
>
> Playwright serve dal pomeriggio. Se a casa **non** l'avete installato (era il Livello 0 del compito di martedì), lanciate **appena arrivati** i comandi del punto 2: il download è lungo e va avanti da solo mentre lavorate sui lab della mattina.

Oggi lavorate sullo **stesso repository** della Bottega di martedì.

## 1. Il punto di partenza

**Avete consegnato il compito della G1?** Lavorate sul vostro repository, su un branch nuovo:

```bash
git switch -c g2
```

**Il vostro `app.py` è ancora rotto?** Per la mattina non è un problema: i test rossi dei sad path sono proprio i bug del compito, e li riconoscerete. Per il pomeriggio, se preferite partire pulito, in `testing-day7/bottega_start/` c'è la Bottega con le correzioni della G1 già applicate (la pubblico la mattina della lezione: fate `git pull`). Copiatela **fuori** dalla cartella del corso, mettetela sotto Git come martedì e copiateci la vostra cartella `tests/` (le fixture di `tests/conftest.py` servono anche oggi).

> In `bottega_start/` la correzione del corriere (`spedizioni.py` e il `503` nel checkout di `app.py`) **non** c'è: è l'esercizio del Lab 3 di stamattina. Dal pomeriggio si tocca **solo il frontend** (`static/`).

## 2. Le dipendenze nuove

Con il venv attivo:

```bash
pip install pytest-playwright==0.10.0 playwright==1.64.1 axe-playwright-python==0.1.8
python -m playwright install chromium
```

Aggiungete le tre righe a `requirements.txt` (le trovate già in `bottega_start/requirements.txt`). Se avete installato Playwright a casa, il primo comando allinea le versioni a quelle del corso e il secondo scarica il browser solo se manca.

Verifica:

```bash
python -m playwright --version          # Version 1.64.1
pytest -VV                              # tra i plugin deve comparire pytest-playwright-0.10.0
```

### Piano B: il download del browser non va

Il browser di Playwright pesa qualche centinaio di MB e la rete dell'aula, con 20 persone insieme, soffre. Se `playwright install chromium` non finisce, potete usare il **Chrome o Edge già installato** sul vostro PC (va scaricato solo il pacchetto Python):

```bash
pytest tests/e2e --browser-channel chrome      # Google Chrome installato
pytest tests/e2e --browser-channel msedge      # Microsoft Edge (preinstallato su Windows)
```

Per non doverlo scrivere ogni volta, aggiungetelo in `pytest.ini`, alla riga `addopts`: `addopts = -m "not chaos" --browser-channel chrome`.

## 3. Accendete il sistema (come martedì)

Due terminali con il venv attivo, nella cartella `bottega/`:

| Terminale | Comando |
|-----------|---------|
| 1 | `python corriere.py` |
| 2 | `python app.py` |

Aprite http://localhost:8000 e fate un acquisto a mano. Teneteli accesi tutto il giorno: servono ai test della mattina, al registratore (`codegen`) e alla pagina. I test del pomeriggio li riusano (se li trovano spenti, li accendono da soli).

## 4. Il primo segno di vita

Nel terzo terminale (lo facciamo insieme all'inizio del pomeriggio):

```bash
python -m playwright codegen localhost:8000
```

Si aprono due finestre: un browser e il **Playwright Inspector**. Fate login e aggiungete un prodotto: il codice Python si scrive da solo. Chiudete tutto quando avete visto il codice comparire.

## Problemi frequenti

| Sintomo | Causa | Soluzione |
|---------|-------|-----------|
| `Executable doesn't exist at .../ms-playwright/...` | Il browser non è stato scaricato, o è di un'altra versione di Playwright | `python -m playwright install chromium`, oppure il piano B |
| `fixture 'page' not found` | `pytest-playwright` non è installato in **questo** venv | `pip install pytest-playwright==0.10.0` con il venv attivo |
| `playwright: command not found` | La cartella degli script del venv non è nel PATH | Usate sempre `python -m playwright ...` |
| Su Linux / WSL: mancano librerie di sistema | Il browser ha bisogno di librerie che il sistema non ha | `python -m playwright install --with-deps chromium` |
| `Address already in use` | Avete lanciato `app.py` due volte | Chiudete il secondo terminale: i test riusano il server già acceso |
