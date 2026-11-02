# LAB 2 — Token, fixture e stato distribuito

## Contesto

Per testare il carrello bisogna prima fare il login. Se copiate le 5 righe del login in ogni test, avrete 30 copie dello stesso codice: alla prima modifica dell'endpoint di login, 30 test da sistemare a mano. **Questo è codice legacy scritto oggi.**

La soluzione industriale si chiama **fixture**: una funzione che *prepara* qualcosa e lo *consegna* al test che lo chiede per nome.

```python
import pytest

@pytest.fixture
def token():
    # ... fa il login e restituisce il token
    return "abc123"

def test_qualcosa(token):          # <- pytest vede il parametro 'token',
    assert token == "abc123"       #    esegue la fixture e vi passa il risultato
```

Le fixture vanno in un file speciale, `tests/conftest.py`. pytest lo carica da solo e le rende disponibili a **tutti** i file di test, senza import.

> 📖 **Parole da sapere per questo lab:**
> [autenticazione e token](../../CONCETTI_BASE.md#autenticazione-e-token) ·
> [header](../../CONCETTI_BASE.md#header) ·
> [fixture](../../CONCETTI_BASE.md#fixture-pytest) ·
> [status code 401](../../CONCETTI_BASE.md#status-code)
>
> **In due righe:** il login vi restituisce un "braccialetto" (il token). Da quel momento, ogni richiesta al carrello deve mostrarlo nell'header `Authorization`, altrimenti il server risponde 401 ("non so chi sei").

**File da creare:** `bottega/tests/conftest.py` e `bottega/tests/test_carrello.py`
**Prerequisito:** `python app.py` acceso (e `python corriere.py` per il Livello 3).

## Livello 1: Sopravvivenza (obbligatorio per tutti)

1. In `conftest.py` create:
   - la fixture `base_url`, che restituisce `"http://localhost:8000"`;
   - la fixture `token`, che fa il login come `mario` e restituisce il token;
   - la fixture `auth`, che **usa** `token` e restituisce `{"Authorization": f"Bearer {token}"}`. Sì: una fixture può chiedere un'altra fixture.
2. Test parametrizzato: `GET /api/carrello` **senza** autenticazione → 401. Casi:
   - nessun header;
   - `Bearer token-inventato`;
   - `token-senza-bearer`.
3. Test: `POST /api/carrello` con `{"prodotto_id": 2, "quantita": 2}` → 201.

> 🧩 **Non sai da dove partire?** Lo scheletro della fixture `token`:
>
> ```python
> # tests/conftest.py
> import pytest
> import requests
>
> @pytest.fixture
> def base_url():
>     return "http://localhost:8000"
>
> @pytest.fixture
> def token(base_url):                       # <- chiede a pytest la fixture base_url
>     risposta = requests.post(
>         f"{base_url}/api/login",
>         json={"username": "???", "password": "???"},   # gli utenti sono nel README della Bottega
>         timeout=5,
>     )
>     return risposta.json()["???"]           # guardate cosa risponde il login nel README
> ```
>
> **Verifica rapida:** scrivete un test che riceve `token` e fa solo `print(token)`, poi lanciate `pytest -s`. Se vedete una stringa di lettere e numeri, la fixture funziona.

## Livello 2: Ingegneria (standard)

1. **Non fidatevi della risposta.** Il `POST` ha detto 201, ma il carrello è stato aggiornato davvero? Scrivete un test che aggiunge un prodotto e poi **verifica lo stato con un'altra chiamata** (`GET /api/carrello`): righe, quantità e totale.

2. **L'isolamento.** Lanciate `pytest` due volte di fila. Qualcosa cambia? Il server ha **memoria**: i test di prima lasciano sporco il carrello per i test dopo. Risolvete con una fixture in `conftest.py`:

   ```python
   @pytest.fixture(autouse=True)
   def stato_pulito(base_url):
       # chiamata a POST /api/reset
       ...
   ```

   `autouse=True` vuol dire "eseguila prima di **ogni** test, anche se nessuno la chiede".

3. **Sad paths del carrello.** Con **un solo** test parametrizzato (`body, status_atteso`) coprite questi casi:

   | Caso | Body | Atteso (contratto) |
   |------|------|--------------------|
   | Quantità negativa | `{"prodotto_id": 2, "quantita": -3}` | 400 |
   | Quantità zero | `{"prodotto_id": 2, "quantita": 0}` | 400 |
   | Tipo sbagliato | `{"prodotto_id": 2, "quantita": "2"}` | 400 |
   | Campo mancante | `{"prodotto_id": 2}` | 400 |
   | Prodotto inesistente | `{"prodotto_id": 999, "quantita": 1}` | 404 |
   | Oltre lo stock | `{"prodotto_id": 3, "quantita": 99}` | 409 |

4. **Sicurezza.** Il contratto dice che un login fallito risponde **sempre** `"credenziali non valide"`, sia con utente inesistente sia con password sbagliata. Verificatelo. Perché è importante?

## Livello 3: Escalation (per chi vuole l'eccellenza)

1. **Flusso completo (end-to-end via API).** Leggete lo stock del prodotto 1, mettetene 2 nel carrello e fate il checkout con CAP `50100`. Poi verificate:
   - status 201;
   - totale `179.80` (spedizione gratuita sopra 50€);
   - lo stock è sceso di 2;
   - il carrello è vuoto.
2. **L'esperimento del ladro.** Con l'app così com'è: aggiungete `quantita: -3` del prodotto 2 (mouse), aggiungete 1 tastiera (prodotto 1) e fate il checkout. Poi rileggete lo stock del mouse. Cosa è successo al magazzino? Scrivetelo nel bug report con una stima della **gravità**.
3. **`scope`.** Il server è acceso? Verificarlo prima di ogni test è uno spreco. Create una fixture con `scope="session"` che controlla `/api/health` **una volta sola**, e se il server è spento ferma tutto con un messaggio chiaro (`pytest.exit("...")`).

## Documentazione

- Fixture di pytest: https://docs.pytest.org/en/stable/how-to/fixtures.html
- conftest.py: https://docs.pytest.org/en/stable/reference/fixtures.html#conftest-py-sharing-fixtures-across-multiple-files
- Autenticazione Bearer (MDN): https://developer.mozilla.org/en-US/docs/Web/HTTP/Authentication
- OWASP, enumerazione degli utenti: https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account
