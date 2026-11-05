# Homework: il corriere e il browser

## Contesto

Oggi avete fatto due cose. La mattina avete finito il lavoro di martedì: i test isolati con `stato_pulito`, e il corriere esterno che senza timeout può bloccare tutta la Bottega. Il pomeriggio avete messo un browser robot davanti alla Bottega e avete scoperto che alcuni bottoni non erano bottoni e alcuni campi non avevano un nome: chi non vede lo schermo, o non usa il mouse, non poteva comprare.

Il compito chiude questi due lavori. **Il Livello 1 è obbligatorio** e, se in aula avete finito il Livello 1 dei lab, richiede circa un'ora e mezza. Con il Livello 2 si arriva a circa tre ore. I tempi tra parentesi sono indicativi.

## Livello 1: Sopravvivenza (obbligatorio per tutti)

1. **Il corriere** ([`testing-day6/lab3_dipendenze_esterne/README.md`](../../testing-day6/lab3_dipendenze_esterne/README.md)), **fino al Livello 2 compreso** (circa 60'):
   - `tests/test_spedizioni.py` con i test con il mock: costo letto dalla risposta, timeout di al massimo 3 secondi, `Timeout` e `ConnectionError` che diventano `ServizioSpedizioniNonDisponibile`, il `503` del corriere;
   - la correzione di `spedizioni.py` (timeout ed eccezione di dominio) e del checkout in `app.py` (`503` con `{"errore": "servizio spedizioni non disponibile"}`);
   - `pytest tests/test_spedizioni.py` verde **con corriere e app spenti**.
2. **Il test E2E del flusso d'acquisto** (lab del pomeriggio, [`lab1_primo_e2e/README.md`](../lab1_primo_e2e/README.md), **Livello 1**) (circa 20' se in aula siete arrivati alla correzione dell'HTML):
   - `tests/e2e/test_acquisto.py` con `test_la_home_si_apre` e `test_acquisto_completo`, con i locator per ruolo ed etichetta della tabella del lab;
   - l'HTML corretto (`<label>` per Username, Password e CAP; `<button>` per "Aggiungi" e "Conferma ordine", con il `submit` del form);
   - `pytest tests/e2e` verde, in headless, **due volte di fila**.
3. **Il bug report** (circa 10'). Nel `BUG_REPORT.md` della G1 aggiungete, con lo stesso formato:
   - il difetto del corriere: nessun timeout, `500` invece di `503`;
   - una sezione **"Frontend"** con i difetti trovati oggi dal test con i ruoli (campi senza etichetta, bottoni fatti con un `<div>`). Per ognuno scrivete **quale test** l'ha trovato.
4. Un commit per ogni gruppo di correzioni, con il codice del bug nel messaggio (es. `fix: BUG-012 bottoni del catalogo non raggiungibili da tastiera`).

## Livello 2: Ingegneria (standard)

1. **L'esperimento di chaos** (Lab 3 di martedì, **Livello 3, punti 1-3**) (circa 20'): il test `@pytest.mark.chaos` che fa il checkout e verifica `503`, tempo sotto i 4 secondi e carrello ancora pieno. Con il **corriere spento**, `pytest -m chaos` deve essere verde. È lo stesso esperimento che avete visto fare in aula: ora lo scrivete voi.
2. **Lo scanner** (lab del pomeriggio, **Livello 2, punti 1-2**) (circa 30'): `tests/e2e/test_accessibilita.py` con axe, che asserisce **zero violazioni `critical` e `serious`** e quando fallisce dice **quali** regole e **quali** elementi. Correggete `lang`, `alt` e i design token del contrasto. Nel bug report aggiungete i difetti che ha trovato axe, con il criterio WCAG (1.1.1 *Contenuti non testuali*, 1.4.3 *Contrasto minimo*, 3.1.1 *Lingua della pagina*).
3. **Il Page Object Model** (lab del pomeriggio, **Livello 2, punto 3**) (circa 40'): `tests/e2e/pagina_bottega.py`, la fixture `bottega` in `conftest.py`, e `test_acquisto_completo` riscritto con il Page Object. `accedi()` torna solo quando compare il saluto.

Vincoli (Quality Gate):
- nei file `test_*.py` dei test E2E non compare nessun `get_by_...` né `page.locator(...)`: i locator vivono solo in `pagina_bottega.py`;
- **vietati** `time.sleep()` e `wait_for_timeout()` in qualsiasi file di test. Un `grep` in fase di correzione li troverà;
- in `app.py` nessuna eccezione di `requests` arriva fino al checkout: lì si gestisce solo `ServizioSpedizioniNonDisponibile`.

## Livello 3: Escalation (facoltativo, sceglietene quanti volete)

- **Il flusso completo via API** (Lab 2 di martedì, Livello 3): lo stock scende, il carrello si svuota; l'esperimento del ladro; la fixture `scope="session"` che controlla il server una volta sola.
- **Il corriere lento** (Lab 3 di martedì, Livello 3, esperimento B) con la tabella "prima / dopo la correzione".
- **I sad path, la tastiera e axe dopo il login** (lab del pomeriggio, Livello 3).
- **Gli errori nell'interfaccia** ([`lab3_debugging_chaos_ui/README.md`](../lab3_debugging_chaos_ui/README.md)): `page.route` e il Trace Viewer, il catalogo che risponde `500`, la funzione `chiamaApi`.
- **La pipeline E2E:** un workflow GitHub Actions (`.github/workflows/e2e.yml`) che installa il browser con `python -m playwright install --with-deps chromium`, accende corriere e app in background, aspetta che rispondano (il ciclo con `curl`, non `sleep 10`) e lancia `pytest tests/e2e` in headless.

---

## Istruzioni per la consegna

1. Lavorate sullo **stesso repository privato** della G1, il docente è già collaboratore. Controllate che `test-results/` **non** sia nel repo.
2. Mandate a `angeligiovanni21@gmail.com` il link al repository (e, se avete fatto la pipeline, il link alla run di GitHub Actions) entro le **23:59 di lunedì 9 novembre**.
