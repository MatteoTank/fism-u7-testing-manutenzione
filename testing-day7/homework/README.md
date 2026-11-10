# Homework: il corriere

## Contesto

Venerdì abbiamo finito il Lab 2 e abbiamo aperto il Lab 3: la Bottega dipende da SpediVeloce, un servizio di un'altra azienda, e per testare il nostro codice senza dipendere dal loro server usiamo un mock. Il compito chiude il Lab 3 fino al Livello 2: cosa succede alla Bottega quando il corriere **non risponde**, e come la si mette al sicuro.

> 📌 **Aggiornamento:** questo compito sostituisce la versione pubblicata giovedì sera, che chiedeva anche un test con il browser. Quella parte non la fate: in aula non ci siamo arrivati.

**Il Livello 1 è obbligatorio** e richiede circa un'ora e mezza. I tempi tra parentesi sono indicativi. Se vi bloccate, scrivete nel README del repository **dove** vi siete bloccati e **cosa** avete provato: conta anche quello.

> 🧩 **Prima di iniziare:** ripassate il `@patch` del semestre 1 (`RECAP_SEMESTRE_1.md`) e il punto 5 di [`sommario_lezione_7.md`](../sommario_lezione_7.md). Il codice di partenza aggiornato è in [`../bottega_start/`](../bottega_start/): ha le correzioni di `app.py` dei Lab 1 e 2, **non** quelle di `spedizioni.py` (quelle sono il compito).

## Livello 1: Sopravvivenza (obbligatorio per tutti)

Tutto il lavoro è nel [Lab 3 di martedì](../../testing-day6/lab3_dipendenze_esterne/README.md). File da creare: `tests/test_spedizioni.py`. Ricordatevi la `stato_pulito` vuota in cima al file (è spiegato nel lab).

1. **Il primo mock** (Livello 1 del lab, circa 20'):
   - `test_costo_letto_dalla_risposta`: con una risposta finta `{"costo": 4.9}`, `costo_spedizione("50100", 1.5)` restituisce `4.9`;
   - un test che con `mock_get.call_args` verifica che al corriere arrivino il CAP e il peso giusti.
2. **I guasti** (Livello 2 del lab, punti 1-3, circa 40'). Prima i test, che saranno **rossi**:
   - il `timeout` di al massimo 3 secondi nella chiamata;
   - `requests.Timeout` e `requests.ConnectionError` (un solo test parametrizzato) che diventano `ServizioSpedizioniNonDisponibile`;
   - il corriere che risponde `503` che diventa anche lui `ServizioSpedizioniNonDisponibile`.

   > 🧩 Appena scrivete `from spedizioni import ServizioSpedizioniNonDisponibile`, pytest si ferma con un **errore di collection** (`ImportError`): la classe non esiste ancora. È normale. Create in `spedizioni.py` la classe vuota (`class ServizioSpedizioniNonDisponibile(Exception): pass`) e i test diventano finalmente **rossi**, cioè pronti per la correzione.
3. **La correzione** (Livello 2 del lab, punto 4, circa 20'): correggete `spedizioni.py` finché i test diventano verdi, poi il checkout in `app.py` (`503` con `{"errore": "servizio spedizioni non disponibile"}`).
4. **La prova:** `pytest tests/test_spedizioni.py` verde **con app e corriere spenti**. Poi, con app e corriere accesi, `pytest` verde anche per i test dei Lab 1 e 2.
5. **Il bug report** (circa 10'). Nel `BUG_REPORT.md` della G1 aggiungete, con lo stesso formato, il difetto del corriere: nessun timeout, `500` invece di `503`. Scrivete **quale test** l'ha trovato.
6. Un commit per ogni passo, con un messaggio che dica cosa avete fatto (es. `test: guasti del corriere (rossi)`, poi `fix: timeout ed eccezione di dominio in spedizioni.py`).

## Livello 2 e 3: per chi vuole andare oltre (facoltativi)

- **L'esperimento di chaos** (Lab 3, Livello 3): il test `@pytest.mark.chaos` che fa il checkout e verifica `503`, tempo sotto i 4 secondi e carrello ancora pieno. Con il **corriere spento** e poi **lento** (`CORRIERE_LATENZA=10`), prima e dopo la vostra correzione, con la tabella dei risultati.
- **Il flusso completo e il ladro** ([Lab 2, Livello 3](../../testing-day6/lab2_autenticazione/README.md)): lo stock scende e il carrello si svuota dopo il checkout; l'esperimento della quantità negativa; la fixture `scope="session"` che controlla il server una volta sola.

---

## Istruzioni per la consegna

1. Lavorate sullo **stesso repository privato** della G1: il docente è già collaboratore.
2. Mandate a `angeligiovanni21@gmail.com` il link al repository entro le **23:59 di lunedì 9 novembre**.
