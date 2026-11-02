# LAB 3 — Il fornitore vi tradirà

## Contesto

Il checkout della Bottega chiede il costo di spedizione a **SpediVeloce**, un servizio di un'altra azienda. Aprite `bottega/spedizioni.py`: sono 3 righe e sembrano innocue.

Domanda: **cosa succede alla Bottega se SpediVeloce si spegne? E se diventa lento?**

Due strumenti per rispondere, uno per ogni livello della piramide:

| | Mock (white box) | Esperimento (black box) |
|---|---|---|
| Cosa rompo | La funzione `requests.get`, **dentro** il processo | Il corriere **vero**, sulla rete |
| Velocità | Millisecondi | Secondi |
| Cosa dimostra | Che **il mio codice** reagisce bene al guasto | Che **il sistema intero** reagisce bene al guasto |

Il primo lo conoscete già dal semestre 1. Il secondo ha un nome: **Chaos Engineering**. Oggi ne facciamo un assaggio.

> 📖 **Parole da sapere per questo lab:**
> [servizio esterno](../../CONCETTI_BASE.md#servizio-esterno-dipendenza) ·
> [timeout](../../CONCETTI_BASE.md#timeout) ·
> [mock](../../CONCETTI_BASE.md#mock) ·
> [eccezione](../../CONCETTI_BASE.md#eccezione) ·
> [sistema distribuito](../../CONCETTI_BASE.md#sistema-distribuito)
>
> **In due righe:** la nostra cucina (la Bottega) dipende da un fornitore (il corriere). Oggi scopriamo cosa succede quando il fornitore non consegna, o consegna con 10 secondi di ritardo.

**File da creare:** `bottega/tests/test_spedizioni.py`
**Prerequisito:** nessun server acceso: con i mock non servono!

> ⚠️ La fixture `stato_pulito` con `autouse=True` del Lab 2 chiama il server prima di ogni test. Questi test non devono dipendere dal server, quindi ridefinitela **nel file** come fixture vuota con lo stesso nome (`yield`). La fixture più vicina al test vince.

## Livello 1: Sopravvivenza (obbligatorio per tutti)

Ricordate la **regola del path**: si intercetta dove la cosa **viene usata**, non dove è definita.

```python
from unittest.mock import patch, MagicMock
import spedizioni

@patch("spedizioni.requests.get")       # requests.get COME LO VEDE spedizioni.py
def test_costo_letto_dalla_risposta(mock_get):
    # Arrange: costruisco una risposta HTTP finta
    risposta_finta = MagicMock()
    risposta_finta.status_code = 200
    risposta_finta.json.return_value = {"costo": 4.9}
    mock_get.return_value = risposta_finta
    # Act ... Assert ...
```

1. Completate il test: `costo_spedizione("50100", 1.5)` deve restituire `4.9`.
2. Verificate che al corriere arrivino i parametri giusti: `mock_get.call_args` vi dice **con cosa** è stato chiamato il mock.

## Livello 2: Ingegneria — iniezione di guasti

Con `side_effect` il mock invece di rispondere **esplode**:

```python
mock_get.side_effect = requests.Timeout("il corriere non risponde")
```

Scrivete prima i test e poi correggete il codice (test rosso → codice → test verde):

1. **Il timeout.** Un test che verifica che `requests.get` venga chiamato con un `timeout` di **al massimo 3 secondi**, come da contratto. Oggi è rosso, perché il timeout non c'è.
2. **L'errore di dominio.** Un test parametrizzato con `requests.Timeout` e `requests.ConnectionError`. In entrambi i casi `costo_spedizione` deve sollevare un'eccezione **vostra**: `ServizioSpedizioniNonDisponibile`.
   > Perché non lasciare passare il `requests.Timeout` così com'è? Perché `app.py` non deve sapere **come** comunichiamo con il corriere. Oggi è HTTP, domani potrebbe essere una coda di messaggi. Il resto del sistema deve parlare la lingua del business: "il servizio spedizioni non è disponibile".
3. **Il 503.** Il corriere risponde, ma con un errore (`status_code = 503`). Anche qui → `ServizioSpedizioniNonDisponibile`.
   *Suggerimento:* `risposta.raise_for_status()` solleva `requests.HTTPError` se lo status è ≥ 400. Nel mock dovete simularlo con `risposta_finta.raise_for_status.side_effect = requests.HTTPError("503")`.
4. **La correzione.** Modificate `spedizioni.py` finché i test diventano verdi. Poi modificate `app.py`: il checkout deve catturare `ServizioSpedizioniNonDisponibile` e rispondere **503** con `{"errore": "servizio spedizioni non disponibile"}`.

## Livello 3: Escalation — il primo esperimento di Chaos Engineering

I mock dimostrano che **la funzione** si comporta bene. Ma il sistema intero? Lo verifichiamo rompendo l'ambiente **per davvero**.

**Ipotesi:** *"Se il corriere è guasto, la Bottega risponde 503 in meno di 4 secondi e il cliente non perde il carrello."*

1. Scrivete un test black box (HTTP, con le fixture del Lab 2) che:
   - mette un prodotto nel carrello;
   - fa il checkout con `timeout=15` lato test;
   - verifica: status 503, `risposta.elapsed.total_seconds() < 4`, carrello ancora pieno.
2. Marcatelo con `@pytest.mark.chaos`. Il `pytest.ini` è già configurato per **escluderlo** dalle esecuzioni normali. Si lancia solo con:

   ```bash
   pytest -m chaos
   ```

3. **Esperimento A — il corriere muore.** Fermate `corriere.py` (CTRL+C) e lanciate `pytest -m chaos`.
4. **Esperimento B — il corriere rallenta.** Riavviatelo con 10 secondi di latenza:

   ```bash
   # Mac/Linux
   CORRIERE_LATENZA=10 python corriere.py
   # Windows (PowerShell) — ricordatevi poi di toglierla: Remove-Item Env:CORRIERE_LATENZA
   $env:CORRIERE_LATENZA=10; python corriere.py
   ```

5. Fate entrambi gli esperimenti **prima** e **dopo** la vostra correzione, e annotate i risultati in una tabella:

   | Scenario | Prima della fix | Dopo la fix |
   |----------|-----------------|-------------|
   | Corriere spento | ? | ? |
   | Corriere lento (10s) | ? | ? |

   Lo scenario "lento" di solito sorprende. Perché un sistema lento è **peggio** di un sistema spento?

## Documentazione

- unittest.mock (`side_effect`, `call_args`): https://docs.python.org/3/library/unittest.mock.html
- requests, timeout: https://requests.readthedocs.io/en/latest/user/advanced/#timeouts
- requests, eccezioni: https://requests.readthedocs.io/en/latest/api/#exceptions
- Marker di pytest: https://docs.pytest.org/en/stable/how-to/mark.html
- Principles of Chaos Engineering: https://principlesofchaos.org/
