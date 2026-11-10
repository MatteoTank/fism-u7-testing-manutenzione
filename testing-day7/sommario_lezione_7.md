# RECAP GIORNO 7: test isolati e il primo mock su un servizio esterno

Oggi abbiamo ripassato con calma quello che serve per andare avanti (client e server, status code, fixture) e abbiamo finito il Lab 2 di martedì: test che non si fidano della risposta, test che non dipendono dall'ordine in cui girano, tanti casi con un solo test. Alla fine abbiamo aperto il Lab 3: la Bottega dipende da un servizio di un'altra azienda, il corriere, e per testarla senza dipendere da lui serve un mock. Di seguito i concetti e i pattern della giornata.

---

## 1. Non fidatevi della risposta: rileggete lo stato

Il `POST` dice `201`, ma il carrello è cambiato davvero? Si verifica con **un'altra chiamata**. È il modo di lavorare con un sistema a scatola nera: non guardo dentro il server, gli faccio una seconda domanda.

```python
def test_aggiunta_visibile_leggendo_il_carrello(base_url, auth):
    # Arrange: aggiungo 2 mouse (34.50 l'uno)
    requests.post(f"{base_url}/api/carrello", json={"prodotto_id": 2, "quantita": 2}, headers=auth, timeout=5)

    # Act: rileggo lo stato con un'ALTRA chiamata
    carrello = requests.get(f"{base_url}/api/carrello", headers=auth, timeout=5).json()

    # Assert
    assert len(carrello["righe"]) == 1
    assert carrello["righe"][0]["quantita"] == 2
    assert carrello["totale"] == 69.00
```

---

## 2. Il server ha memoria: test isolati

Il test qui sopra, lanciato insieme agli altri, è diventato rosso con `assert 4 == 2`. Non era sbagliato: un test precedente aveva già messo 2 mouse nel carrello, e il server se li ricordava.

Un test che passa o fallisce **in base all'ordine** o a **quante volte** lo lanci è un **test flaky**: il nemico numero uno di una CI. La cura: ogni test parte da uno stato noto.

```python
# tests/conftest.py
@pytest.fixture(autouse=True)          # autouse: gira prima di OGNI test, anche se nessuno la chiede
def stato_pulito(base_url):
    requests.post(f"{base_url}/api/reset", timeout=5)
```

- `POST /api/reset` riporta i dati allo stato iniziale. Esiste **solo** per i test (il contratto lo dice).
- Il reset cancella anche i token. Non è un problema: `stato_pulito` gira **prima** di `token`, quindi ogni test fa un login nuovo.

> 🧩 **Se vi perdete con le fixture:** una fixture è una funzione che prepara qualcosa per il test. Il test la "chiede" scrivendone il nome tra i parametri; pytest la esegue prima e gli passa il risultato. Con `autouse=True` non serve chiederla: gira sempre.

---

## 3. Un test, tanti casi: `parametrize`

I sad path del carrello sono sei casi con la stessa struttura. Si scrivono **una volta sola**:

```python
@pytest.mark.parametrize(
    "body, status_atteso",
    [
        ({"prodotto_id": 2, "quantita": -3}, 400),   # quantità negativa
        ({"prodotto_id": 2, "quantita": 0}, 400),    # quantità zero
        ({"prodotto_id": 2, "quantita": "2"}, 400),  # tipo sbagliato
        ({"prodotto_id": 2}, 400),                   # campo mancante
        ({"prodotto_id": 999, "quantita": 1}, 404),  # prodotto inesistente
        ({"prodotto_id": 3, "quantita": 99}, 409),   # oltre lo stock
    ],
)
def test_aggiunta_al_carrello_sad_paths(base_url, auth, body, status_atteso):
    risposta = requests.post(f"{base_url}/api/carrello", json=body, headers=auth, timeout=5)
    assert risposta.status_code == status_atteso
```

Con l'`app.py` originale i primi quattro casi sono rossi: sono bug veri. Una quantità negativa accettata vuol dire, al checkout, uno stock che **aumenta**.

---

## 4. Sicurezza: il login non deve dire troppo

Il contratto dice che un login fallito risponde **sempre** `"credenziali non valide"`. Se il messaggio cambia tra "utente inesistente" e "password errata", un attaccante prova mille nomi e scopre quali utenti esistono (si chiama *user enumeration*). Poi gli resta solo da indovinare la password.

```python
@pytest.mark.parametrize("username, password", [
    ("utente_che_non_esiste", "qualcosa"),   # utente inesistente
    ("mario", "password_sbagliata"),         # utente vero, password sbagliata
])
def test_login_fallito_non_rivela_se_utente_esiste(base_url, username, password):
    risposta = requests.post(f"{base_url}/api/login", json={"username": username, "password": password}, timeout=5)
    assert risposta.status_code == 401
    assert risposta.json()["errore"] == "credenziali non valide"
```

---

## 5. Il corriere e il primo mock

Il checkout chiede il costo di spedizione a **SpediVeloce**, un servizio di un'altra azienda (`bottega/spedizioni.py`). Per testare il **nostro** codice non vogliamo dipendere dal **loro** server: lo sostituiamo con un mock. È esattamente il `@patch` del semestre 1 (`RECAP_SEMESTRE_1.md`): cambia solo il bersaglio, che ora è una chiamata di rete.

```python
from unittest.mock import patch, MagicMock
import spedizioni

@patch("spedizioni.requests.get")        # REGOLA DEL PATH: dove viene USATO, non dove è definito
def test_costo_letto_dalla_risposta(mock_get):
    # Arrange: una risposta HTTP finta
    risposta_finta = MagicMock()
    risposta_finta.status_code = 200
    risposta_finta.json.return_value = {"costo": 4.9}
    mock_get.return_value = risposta_finta

    # Act
    costo = spedizioni.costo_spedizione("50100", 1.5)

    # Assert
    assert costo == 4.9
```

- **`return_value`**: "quando ti chiamano, rispondi questo".
- **`call_args`**: "con quali parametri ti hanno chiamato?".
- Questi test **non hanno bisogno di nessun server acceso**: girano in millisecondi.

**⚠️ Attenzione:** la `stato_pulito` con `autouse=True` chiama il server prima di **ogni** test, anche di quelli con il mock. Nel file dei test con il mock si ridefinisce vuota, con lo stesso nome: vince la fixture più vicina al test.

```python
@pytest.fixture(autouse=True)
def stato_pulito():
    yield
```

Il resto del Lab 3 (cosa succede quando il corriere **non risponde**) è nel compito.

---

## 6. Documentazione Ufficiale (RTFM)

- **Pytest Fixture:** https://docs.pytest.org/en/stable/how-to/fixtures.html
- **Pytest parametrize:** https://docs.pytest.org/en/stable/how-to/parametrize.html
- **unittest.mock (patch, MagicMock):** https://docs.python.org/3/library/unittest.mock.html
- **Dove applicare il patch:** https://docs.python.org/3/library/unittest.mock.html#where-to-patch
- **OWASP, Account Enumeration:** https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/03-Identity_Management_Testing/04-Testing_for_Account_Enumeration_and_Guessable_User_Account
