# LAB 3 — Debugging e chaos lato browser

> **Facoltativo: in aula non lo facciamo.** È un esercizio in più per chi ha finito il compito e vuole andare avanti (Livello 3 del compito, `homework/README.md`).
> Prima di iniziare vi servono: il Lab 3 di martedì finito (il checkout che risponde `503` quando il corriere è giù), l'HTML corretto del lab del pomeriggio e il Page Object (`pagina_bottega.py`, Livello 2 di [`lab1_primo_e2e`](../lab1_primo_e2e/README.md)). Gli strumenti nuovi (`page.route`, Trace Viewer) sono spiegati qui sotto e nella documentazione in fondo.

> 📖 **Parole da sapere per questo lab** (spiegate con esempi in [`CONCETTI_BASE.md`](../../CONCETTI_BASE.md)): [frontend e backend](../../CONCETTI_BASE.md#frontend-e-backend) · [status code](../../CONCETTI_BASE.md#status-code) · [timeout](../../CONCETTI_BASE.md#timeout) · [mock](../../CONCETTI_BASE.md#mock)

## Contesto

Con il Lab 3 di martedì avete reso **robusto il backend**: se SpediVeloce è giù, la Bottega risponde `503` in 3 secondi invece di esplodere. Ora fate questa prova: spegnete `corriere.py`, aprite la Bottega nel browser e comprate qualcosa.

Il backend risponde un `503` perfetto, da manuale. E il cliente cosa vede? **Niente.** Nessun messaggio, il bottone non fa niente, il carrello è ancora pieno. L'ordine è passato o no? Il cliente riclicca, oppure chiama il servizio clienti, oppure va su Amazon.

> Un backend robusto con un frontend che ignora gli errori è come un airbag che si apre... nel bagagliaio.

Oggi rompiamo la rete **del browser**, in modo controllato, con `page.route()`:

| G1 (Lab 3) | Oggi |
|---|---|
| `@patch("spedizioni.requests.get")` | `page.route("**/api/ordini", ...)` |
| `side_effect = requests.Timeout(...)` | `route.abort("internetdisconnected")` |
| `return_value = risposta finta 503` | `route.fulfill(status=503, json={...})` |
| il guasto lo vede **il backend** | il guasto lo vede **il frontend** |

**File da creare:** `bottega/tests/e2e/test_resilienza.py`
**File da modificare:** `bottega/static/app.js` (e `conftest.py` per la fixture `errori_js`)

## Livello 1: Sopravvivenza (obbligatorio per tutti)

1. **Il catalogo esplode.** Scrivete un test che intercetta `**/api/prodotti`, risponde `500`, apre la pagina e si aspetta un messaggio comprensibile (es. "Non riusciamo a caricare il catalogo") in un elemento con ruolo `alert`.

   ```python
   def test_catalogo_in_errore_500_mostra_un_messaggio(bottega):
       # Arrange: la "rete" del browser risponde 500 al posto del server
       bottega.page.route("**/api/prodotti", lambda route: route.fulfill(status=500, json={"errore": "boom"}))
       # Act
       bottega.apri()
       # Assert
       expect(bottega.avviso_errore).to_contain_text("Non riusciamo a caricare il catalogo")
   ```

   > `page.route()` va chiamato **prima** dell'azione che fa partire la richiesta: è un Arrange.

2. **Debugging: guardate il fallimento, non indovinatelo.** Il test è rosso. Invece di riempire `app.js` di `console.log`, fatevi dare le prove:

   ```bash
   pytest tests/e2e/test_resilienza.py --tracing retain-on-failure --screenshot only-on-failure --video retain-on-failure
   python -m playwright show-trace test-results/<nome-del-test>/trace.zip
   ```

   Nel **Trace Viewer** trovate, passo per passo: le azioni, la pagina **prima e dopo** ogni azione, la scheda **Network** (c'è la vostra risposta 500 finta?) e la scheda **Console**. Cercate l'errore JavaScript: cosa dice, e in quale riga di `app.js`? Annotatelo.

3. **Correggete `app.js`**: `caricaCatalogo()` deve gestire l'errore e mostrare il messaggio.

> 🧩 **Non sai da dove partire?** Il test del punto 1 ce l'avete già. Se il vostro `PaginaBottega` non ha ancora `avviso_errore`, aggiungete nel costruttore:
>
> ```python
> self.avviso_errore = page.get_by_role("???")    # il ruolo dei messaggi di errore urgenti
> ```
>
> Poi lo scheletro di `caricaCatalogo()` in `app.js` per il punto 3:
>
> ```javascript
> async function caricaCatalogo() {
>   const catalogo = document.getElementById("catalogo");
>   let prodotti;
>   try {
>     const risposta = await fetch("/api/prodotti");
>     if (!risposta.???) {                          // fetch NON lancia errori per un 500: controllate voi
>       throw new Error(`errore ${risposta.status}`);
>     }
>     prodotti = await risposta.json();
>   } catch (errore) {
>     catalogo.innerHTML = "";
>     const avviso = document.createElement("p");
>     avviso.className = "errore";
>     avviso.setAttribute("role", "???");           // lo stesso ruolo che cerca il test
>     avviso.textContent = "???";                   // il testo che il test si aspetta
>     catalogo.appendChild(avviso);
>     return;                                       // senza return il codice sotto esplode lo stesso
>   }
>
>   catalogo.innerHTML = "";
>   for (const p of prodotti) {
>     // ... il ciclo che crea le schede, come prima ...
>   }
> }
> ```
>
> **Verifica rapida:** nel Trace Viewer la scheda **Console** non deve più mostrare `prodotti is not iterable`.

## Livello 2: Ingegneria (standard)

1. **Un solo punto per gli errori.** Se mettete un `try/catch` copiato in ogni funzione, state ripetendo l'errore architetturale che nel compito di martedì era vietato nel backend. Scrivete in `app.js` **una** funzione `chiamaApi(url, opzioni)` che:
   - chiama `fetch` e trasforma un errore di rete in un errore leggibile;
   - **controlla `risposta.ok`**: `fetch` NON considera errori i `404` o i `500`, li dovete controllare voi;
   - restituisce i dati JSON o lancia un errore con lo status.

   È il `leggi_json()` della G1, lato browser.

2. **Il checkout con il corriere giù.** Test: login, aggiungo la tastiera, intercetto `**/api/ordini` con un `503` e `{"errore": "servizio spedizioni non disponibile"}`, confermo l'ordine. Verifico che:
   - compaia un `alert` che dice chiaramente che l'ordine **NON** è stato registrato;
   - nella pagina non compaia mai la parola `undefined`;
   - il carrello contenga **ancora** la tastiera.

3. **Gli errori invisibili.** Aggiungete in `conftest.py` una fixture che raccoglie le eccezioni JavaScript non gestite:

   ```python
   @pytest.fixture
   def errori_js(page):
       errori = []
       page.on("pageerror", lambda eccezione: errori.append(str(eccezione)))
       return errori
   ```

   e in fondo ai test del Lab 3 `assert errori_js == []`. Un errore JavaScript non gestito è un bug **anche** se la pagina "sembra" a posto.

4. **Senza rete.** `route.abort("internetdisconnected")` sul catalogo → messaggio "Impossibile contattare il server".

## Livello 3: Escalation (per chi vuole l'eccellenza)

1. **Il cliente impaziente (latenza).** Il checkout ci mette 3 secondi (il corriere lento della G1!). Il cliente clicca "Conferma ordine", non vede niente... e riclicca. Quanti ordini partono?

   Senza `sleep`: "congelate" la rete e decidete voi quando sbloccarla.

   ```python
   in_attesa = []
   bottega.page.route("**/api/ordini", lambda route: in_attesa.append(route))   # la richiesta resta appesa
   # ... confermo l'ordine, verifico lo stato "in corso", riclicco ...
   for route in in_attesa:
       route.continue_()                                                     # ora la "rete" risponde
   ```

   Requisiti: durante l'attesa il bottone è **disabilitato** (`to_be_disabled()`) e un messaggio dice che l'ordine è in corso; un secondo click (`click(force=True)`) **non** fa partire una seconda richiesta (`len(in_attesa) == 1`); alla fine compare la conferma.

2. **Chaos vero, non simulato.** Spegnete `corriere.py` e fate un acquisto dal browser con la vostra `app.js` corretta. Poi riaccendetelo con `CORRIERE_LATENZA=10`. Il messaggio che vede il cliente è quello che vi aspettavate? Mettete a confronto, in una tabella, `page.route` e il guasto vero: cosa dimostra ciascuno?

3. **La 409 dimenticata.** Il contratto prevede `409` quando si chiede più dello stock. Provate a mettere nel carrello 3 monitor (lo stock è 2), un click alla volta. Cosa vede il cliente? Cosa risponde il backend? **Leggete bene**: c'è un bug, ma è nel frontend o nel backend? Scrivetelo nel bug report con le prove.

## Documentazione

- Intercettare la rete (`page.route`, `fulfill`, `abort`, `continue_`): https://playwright.dev/python/docs/network
- API di `Route`: https://playwright.dev/python/docs/api/class-route
- Trace Viewer: https://playwright.dev/python/docs/trace-viewer-intro
- Opzioni `--tracing`, `--screenshot`, `--video` del plugin pytest: https://playwright.dev/python/docs/test-runners#cli-arguments
- Eventi della pagina (`pageerror`, `console`): https://playwright.dev/python/docs/api/class-page#page-event-page-error
- Debug con l'Inspector (`PWDEBUG=1`, `page.pause()`): https://playwright.dev/python/docs/debug
- MDN, `fetch` e `response.ok`: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#checking_that_the_fetch_was_successful
- Principles of Chaos Engineering: https://principlesofchaos.org/
