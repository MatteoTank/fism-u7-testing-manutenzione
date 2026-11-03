# RECAP GIORNO 6: Testing di API REST, la scatola nera distribuita

L'obiettivo di oggi era fare un salto di scala. Nel semestre 1 la scatola nera era un programma sul vostro PC, interrogato con `subprocess`. Oggi la scatola nera è un **server**: un processo separato che si raggiunge solo attraverso la rete. È così che è fatto qualsiasi sistema vero, da un e-commerce alla vostra banca. Di seguito i concetti, i pattern e le regole che abbiamo stabilito.

> 📖 Se qualche parola di questo riepilogo non vi è chiara (client, server, porta, header, JSON, token...), la trovate spiegata con esempi in [`CONCETTI_BASE.md`](../CONCETTI_BASE.md), Parte 1.

---

## 1. HTTP è POSIX con un altro nome

Non abbiamo imparato niente di nuovo: abbiamo **tradotto** quello che sapevate già.

| Semestre 1 (CLI) | Oggi (API REST) |
|------------------|-----------------|
| `subprocess.run([...])` | `requests.get(url)` / `requests.post(url, json=...)` |
| Exit code (`0`, `1`, `2`) | Status code (`200`, `400`, `500`) |
| stdout | body JSON (`risposta.json()`) |
| stderr | `{"errore": "..."}` |

### Le famiglie degli status code: di chi è la colpa?

- **2xx (Successo):** `200 OK` (lettura riuscita), `201 Created` (ho creato qualcosa)
- **4xx (Colpa del client):** `400` dati sbagliati, `401` non so chi sei, `403` so chi sei ma non puoi, `404` non esiste, `409` conflitto con lo stato (es. stock finito)
- **5xx (Colpa del server):** `500` sono esploso, `503` un servizio da cui dipendo non risponde

**⚠️ LA REGOLA D'ORO:** un `500` causato dall'input del client è **sempre** un bug. Il server deve difendersi da qualsiasi spazzatura e rispondere `400`, mai esplodere.

---

## 2. Il Contratto vince sempre

Un test non verifica "quello che secondo me dovrebbe fare il codice". Verifica quello che dice la **specifica** concordata con il cliente (per noi, `bottega/README.md`; in industria spesso è un file OpenAPI/Swagger).

Quando un test è rosso, la domanda giusta non è "come lo faccio diventare verde?", ma: **"chi ha ragione, il codice o il contratto?"**

- Il codice viola il contratto → **bug**, da documentare e correggere
- Il contratto non dice niente su quel caso → **buco nella specifica**, va segnalato al cliente, non inventato

Un test rosso che dimostra un bug non è un fallimento: è un **documento di collaudo**.

---

## 3. L'anatomia di un test di API

```python
import requests

BASE_URL = "http://localhost:8000"

def test_prodotto_esistente():
    # Act
    risposta = requests.get(f"{BASE_URL}/api/prodotti/1", timeout=5)

    # Assert: il contratto, pezzo per pezzo
    assert risposta.status_code == 200                              # lo "exit code"
    assert risposta.headers["Content-Type"] == "application/json"   # il formato
    assert risposta.json()["id"] == 1                               # il contenuto
```

**Le regole di ingaggio:**

- **Ogni chiamata di rete ha un `timeout`.** Senza, un server bloccato blocca anche il vostro test, e la vostra pipeline di CI resta appesa per ore.
- **`json=` per i dati normali, `data=` per mandare spazzatura apposta.** Con `json=` è `requests` a costruire un JSON valido per voi; per testare un JSON rotto serve la stringa grezza.
- **Gli schemi si validano con `jsonschema`, non con 15 `assert` a mano.** Lo schema è una dichiarazione leggibile di cosa vi aspettate.
- **Non fidatevi della risposta: verificate lo stato.** Il `POST` dice 201? Rileggete il carrello con un `GET`. In un sistema distribuito "ho ricevuto ok" e "è successo davvero" sono due cose diverse.

---

## 4. Fixture: l'Arrange scritto una volta sola

Se copiate le righe del login in 30 test, avete scritto 30 punti di rottura. La soluzione industriale è la **fixture**: una funzione che prepara qualcosa e la consegna a chi la chiede **per nome**.

```python
# tests/conftest.py  ->  pytest lo carica da solo, nessun import necessario

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:8000"

@pytest.fixture
def token(base_url):                     # una fixture può usare un'altra fixture
    r = requests.post(f"{base_url}/api/login",
                      json={"username": "mario", "password": "password123"}, timeout=5)
    return r.json()["token"]

@pytest.fixture
def auth(token):
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(autouse=True)            # gira prima di OGNI test, anche se nessuno la chiede
def stato_pulito(base_url):
    requests.post(f"{base_url}/api/reset", timeout=5)
```

```python
# tests/test_carrello.py
def test_carrello_vuoto(base_url, auth):    # il test DICHIARA di cosa ha bisogno
    r = requests.get(f"{base_url}/api/carrello", headers=auth, timeout=5)
    assert r.json()["righe"] == []
```

- **`scope="session"`**: eseguita una volta sola per tutta la sessione di test
- **`scope="function"`** (default): eseguita per ogni test
- **`autouse=True`**: eseguita senza che nessuno la chieda; da usare con parsimonia e sempre documentata

### Isolamento dei test

Un server ha **memoria**. Se il test A lascia un prodotto nel carrello, il test B lo trova lì. Il risultato cambia in base all'ordine di esecuzione: questo è un **test flaky**, il nemico numero uno di una CI. Ogni test deve partire da uno stato noto: per questo esiste la fixture `stato_pulito`.

---

## 5. Cosa manca: il Lab 3

Il terzo laboratorio (il corriere esterno: cosa succede alla Bottega quando un servizio da cui dipende è spento o lento) non l'abbiamo fatto. Lo facciamo **venerdì**, all'inizio della lezione. Se volete arrivare preparati, ripassate il `@patch` del semestre 1 (`RECAP_SEMESTRE_1.md`, sezione 8).

---

## 6. Documentazione Ufficiale (RTFM)

- **requests (Quickstart):** https://requests.readthedocs.io/en/latest/user/quickstart/
- **requests (Timeout):** https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
- **HTTP Status Code (MDN):** https://developer.mozilla.org/en-US/docs/Web/HTTP/Status
- **JSON Schema:** https://json-schema.org/learn/getting-started-step-by-step
- **Pytest Fixture:** https://docs.pytest.org/en/stable/how-to/fixtures.html
- **OWASP, Account Enumeration:** https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account
