# LAB 1 — Il contratto pubblico

## Contesto

Nel semestre 1 testavate una CLI con `subprocess`: input da terminale, poi verifica di exit code e stdout. Oggi la scatola nera è un **server**, e il canale non è il terminale ma la rete. Lo strumento è la libreria `requests`.

| CLI (semestre 1) | API REST (oggi) |
|------------------|-----------------|
| `subprocess.run([...])` | `requests.get(url)` / `requests.post(url, json=...)` |
| `risultato.returncode == 0` | `risposta.status_code == 200` |
| `risultato.stdout` | `risposta.json()` |
| `risultato.stderr` | `risposta.json()["errore"]` |

In questo lab testiamo solo gli endpoint **pubblici**, cioè quelli che non richiedono il login.

> 📖 **Parole da sapere per questo lab** (tutte spiegate in [`CONCETTI_BASE.md`](../../CONCETTI_BASE.md)):
> [client e server](../../CONCETTI_BASE.md#client-e-server) ·
> [URL](../../CONCETTI_BASE.md#url) ·
> [richiesta e risposta HTTP](../../CONCETTI_BASE.md#richiesta-e-risposta-http) ·
> [metodi GET/POST](../../CONCETTI_BASE.md#metodi-http-i-verbi) ·
> [status code](../../CONCETTI_BASE.md#status-code) ·
> [header](../../CONCETTI_BASE.md#header) ·
> [JSON](../../CONCETTI_BASE.md#json) ·
> [API ed endpoint](../../CONCETTI_BASE.md#api-ed-endpoint) ·
> [contratto](../../CONCETTI_BASE.md#contratto-specifica)

**File da creare:** `bottega/tests/test_contratto.py`
**Prerequisito:** `python app.py` acceso.

## Regole di ingaggio

- Ogni chiamata ha un `timeout=5`. Un test senza timeout può bloccarsi per sempre: in CI significa una pipeline appesa per ore.
- Pattern AAA sempre, anche quando il test è di 3 righe.
- Il riferimento è il **README (contratto)**, non il codice di `app.py`. Non aprite `app.py` per capire "cosa dovrebbe fare": siete una scatola nera.

## Livello 1: Sopravvivenza (obbligatorio per tutti)

1. `GET /api/health` → status 200 e `status == "ok"`.
2. `GET /api/prodotti` → status 200, `Content-Type` uguale a `application/json`, lista non vuota.
3. `GET /api/prodotti/1` → status 200 e l'`id` del prodotto restituito è `1`.

> 🧩 **Non sai da dove partire?** Ecco lo scheletro del test 2. Copialo e sostituisci i `???`:
>
> ```python
> import requests
>
> BASE_URL = "http://localhost:8000"
>
> def test_lista_prodotti_non_vuota():
>     # Act: faccio la richiesta, come farebbe il browser
>     risposta = requests.get(f"{BASE_URL}/api/???", timeout=5)
>
>     # Assert: controllo la risposta, pezzo per pezzo
>     assert risposta.status_code == ???
>     assert risposta.headers["Content-Type"] == "???"
>     prodotti = risposta.json()          # il testo JSON diventa una lista Python
>     assert len(prodotti) > ???
> ```
>
> **Trucco:** prima di scrivere il test, aprite l'URL nel browser (http://localhost:8000/api/prodotti). Quello che vedete è esattamente ciò che riceverà `risposta.json()`.

## Livello 2: Ingegneria (standard)

1. **Validazione dello schema.** Controllare a mano ogni campo di ogni prodotto è fragile e verboso. Usate `jsonschema`:

   ```python
   from jsonschema import validate

   SCHEMA_PRODOTTO = {
       "type": "object",
       "properties": {
           "id": {"type": "integer"},
           # ... completate voi seguendo la tabella del README
       },
       "required": [...],
       "additionalProperties": False,
   }

   validate(instance=prodotto, schema=SCHEMA_PRODOTTO)   # se non rispetta lo schema -> eccezione -> test rosso
   ```

   Scrivete un test che valida **ogni** prodotto della lista.

2. **Prodotto inesistente.** Con **un solo** test parametrizzato verificate gli id `999`, `0`, `-1`, `abc`. Il contratto dice: 404, **in JSON**, con la chiave `errore`.

   > Se qualche caso diventa rosso, **non correggete il test**. Leggete il messaggio: avete trovato il vostro primo bug.

## Livello 3: Escalation (per chi vuole l'eccellenza)

**Payload corrotti.** Un attaccante, o un frontend scritto male, manderà al login di tutto. Il contratto dice che un input sbagliato del client dà **400**, mai 500.

Scrivete un test parametrizzato su `POST /api/login` con almeno questi body:

| Caso | Body |
|------|------|
| JSON troncato | `'{"username": "mario"'` |
| Testo libero | `"non sono json"` |
| Body vuoto | `""` |
| Manca la password | `'{"username": "mario"}'` |
| Manca lo username | `'{"password": "password123"}'` |
| JSON del tipo sbagliato | `"[]"` |

> **Attenzione:** con `json=` è `requests` a costruire un JSON valido per voi, quindi non potreste mai mandare un JSON rotto. Qui serve `data=` con la stringa grezza, più l'header `{"Content-Type": "application/json"}`.

**Domanda da annotare nel vostro bug report:** cosa contiene la risposta 500? Provate a salvarla in un file `.html` e ad aprirla nel browser. Perché è un problema di **sicurezza**, oltre che di qualità?

## Documentazione

- requests (Quickstart): https://requests.readthedocs.io/en/latest/user/quickstart/
- HTTP status code (MDN): https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
- JSON Schema (guida introduttiva): https://json-schema.org/learn/getting-started-step-by-step
- jsonschema per Python: https://python-jsonschema.readthedocs.io/en/stable/
