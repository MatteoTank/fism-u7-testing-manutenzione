# LAB DEL POMERIGGIO — Il primo test dal browser (e i bottoni che non esistono)

> 📖 **Parole da sapere per questo lab** (spiegate con esempi in [`CONCETTI_BASE.md`](../../CONCETTI_BASE.md)): [HTML, CSS, JavaScript](../../CONCETTI_BASE.md#html-css-javascript) · [DOM](../../CONCETTI_BASE.md#dom) · [elemento, tag, attributo](../../CONCETTI_BASE.md#elemento-tag-attributo) · [locator](../../CONCETTI_BASE.md#selettore--locator) · [headless](../../CONCETTI_BASE.md#headless) · [fixture](../../CONCETTI_BASE.md#fixture-pytest) · [accessibilità](../../CONCETTI_BASE.md#accessibilità)

> **Oggi in aula si fa solo questo lab.** Il Livello 1 è l'obiettivo della giornata. Il Livello 2 è per chi va veloce, e comunque è nel compito. La cartella `lab2_accessibilita/` rimanda qui; `lab3_debugging_chaos_ui/` è facoltativo e in aula non lo facciamo.

## Contesto

Martedì e stamattina avete testato la Bottega **dal retro**: richieste HTTP dirette all'API, con `requests`. Il cliente vero però non manda JSON: apre un browser, scrive, clicca. Tra lui e l'API c'è un pezzo di codice che finora nessuno ha collaudato: il **frontend** (`static/index.html` e `static/app.js`).

Oggi il test lo fa un browser vero, comandato da Python con **Playwright**.

| Martedì (API) | Oggi (browser) |
|---|---|
| `requests.post(url, json=...)` | `page.get_by_role("button", name="Accedi").click()` |
| `assert risposta.status_code == 201` | `expect(page.get_by_text("Ordine n. 1 confermato!")).to_be_visible()` |
| verifico cosa **risponde il server** | verifico cosa **vede l'utente** |
| fixture `stato_pulito` | la stessa, identica |

C'è una seconda cosa che scoprirete. Playwright cerca gli elementi **come li cerca un lettore di schermo** (il programma che legge la pagina ad alta voce a chi non vede). Se il vostro test non trova il bottone "Aggiungi" per ruolo, non lo trova nemmeno chi usa la Bottega senza vedere lo schermo, e chi usa solo la tastiera non ci arriva. Dal 28 giugno 2025, con l'**European Accessibility Act** (in Italia D.Lgs. 82/2022), un negozio online per i consumatori deve essere accessibile: per la Bottega un difetto di accessibilità è un difetto di **conformità**, come un 500 sull'API.

**File di partenza:** `testing-day7/lab1_primo_e2e/conftest.py` → copiatelo in `bottega/tests/e2e/conftest.py`
**File da creare:** `bottega/tests/e2e/test_acquisto.py`
**File da modificare:** `bottega/static/index.html`, `bottega/static/app.js` (Livello 2 anche `bottega/static/style.css`)
**Prerequisito:** corriere e app accesi, come stamattina. Playwright installato (`SETUP.md`).

## Regole di ingaggio (Quality Gate del lab)

1. **Locator nell'ordine giusto.** Prima `get_by_role`, poi `get_by_label`, poi `get_by_placeholder` / `get_by_text`. CSS (`#id`, `.classe`) e XPath solo se non c'è alternativa, e con un commento che spiega perché.
2. **Vietati `time.sleep()` e `page.wait_for_timeout()`.** Playwright aspetta da solo (*auto-waiting*): ogni azione aspetta che l'elemento sia visibile e cliccabile, ogni `expect()` riprova finché la condizione è vera o scadono 5 secondi.
3. **Le verifiche sulla pagina si fanno con `expect(...)`**, non con `assert locator.inner_text() == ...`: l'`assert` legge il valore **una volta sola**, subito, anche se la pagina non ha ancora finito di aggiornarsi.
4. Pattern AAA, sempre.

## Livello 1: Sopravvivenza (obbligatorio per tutti, in aula)

1. **Il conftest.** Create la cartella `bottega/tests/e2e/` e copiateci `conftest.py`. Leggetelo (5 minuti, non di più). Due cose da capire, non da imparare a memoria:
   - se la Bottega è già accesa, la fixture `server_bottega` la **riusa**; se è spenta, la accende lei e la spegne alla fine;
   - `stato_pulito` è la fixture di stamattina: prima di ogni test il server torna pulito.

2. **Il primo segno di vita.** In `tests/e2e/test_acquisto.py`:

   ```python
   from playwright.sync_api import Page, expect


   def test_la_home_si_apre(page: Page):        # page: la fixture di pytest-playwright
       page.goto("/")                           # solo il percorso: il resto lo mette base_url

       expect(page).to_have_title("La Bottega")
   ```

   ```bash
   pytest tests/e2e --headed --slowmo 500     # il browser si apre e va al rallentatore
   pytest tests/e2e                           # headless: nessuna finestra, è così che gira in CI
   ```

   Deve essere **verde**. Se non lo è, il problema è nel setup, non nel test: chiamate il docente prima di andare avanti.

3. **Il flusso critico, con i locator "da utente".** Nello stesso file scrivete `test_acquisto_completo(page)`:
   - apre la home e fa login come `mario` / `password123`, poi aspetta il saluto `Ciao mario!`;
   - aggiunge al carrello la **Tastiera meccanica** e verifica che compaia `1 × Tastiera meccanica`;
   - fa il checkout con CAP `50100`;
   - verifica che compaia `Ordine n. 1 confermato! Totale pagato: € 89.90` e che il carrello torni vuoto (`Il carrello è vuoto`).

   Usate **questi** locator, cioè quelli con cui un utente descriverebbe la pagina:

   | Elemento | Locator |
   |----------|---------|
   | campo username / password | `page.get_by_label("Username")` / `page.get_by_label("Password")` |
   | bottone "Accedi" | `page.get_by_role("button", name="Accedi")` |
   | bottone "Aggiungi" della Tastiera | `page.locator(".scheda").filter(has_text="Tastiera meccanica").get_by_role("button", name="Aggiungi")` |
   | campo CAP | `page.get_by_label("CAP")` |
   | bottone "Conferma ordine" | `page.get_by_role("button", name="Conferma ordine")` |
   | messaggi e carrello | `page.get_by_text("...")` |

   (Per la scheda del prodotto usiamo una classe CSS perché la scheda non ha un ruolo. Il bottone dentro, invece, deve averlo.)

   Lanciate il test: è **rosso**. Va bene così: non è il test a essere sbagliato, è la pagina.

4. **Leggete cosa non trova.** Il messaggio d'errore dice `waiting for get_by_label("Username")` e poi `Timeout 5000ms exceeded`: il campo c'è, ma **non ha un'etichetta**. Per vedere tutta la pagina come la sente un lettore di schermo, aggiungete questa sonda e lanciatela:

   ```python
   def test_cosa_sente_un_lettore_di_schermo(page: Page):
       page.goto("/")
       # .first: qui ci basta sapere se ne esiste almeno uno
       expect(page.get_by_role("button", name="Aggiungi").first).to_be_visible()
   ```

   Sotto il `Call log` c'è l'**Aria snapshot**. Cercate "Aggiungi": è `text`, non `button`. Annotatevi quali elementi non sono quello che sembrano.

5. **Correggete l'HTML, un elemento alla volta**, rilanciando il test dopo ogni correzione. Il test si ferma ogni volta un passo più avanti.
   - In `index.html`: un `<label for="...">` per i campi Username, Password e CAP. Il placeholder **non** è un'etichetta: sparisce appena scrivete.
   - In `app.js`: il `<div class="btn" onclick=...>Aggiungi</div>` diventa un `<button>`.
   - In `index.html`: il `<div>` "Conferma ordine" diventa un `<button>`, e in `app.js` il checkout parte dall'evento `submit` del form.

   > ⚠️ **Trappola:** un `<button>` dentro un `<form>` è di tipo `submit`. Se cliccate "Conferma ordine" e la pagina si **ricarica**, l'avete trovata. La soluzione: ascoltare l'evento `submit` del form e chiamare `evento.preventDefault()`. Così l'ordine parte anche premendo Invio nel campo CAP.

   Quando il test è **verde**, lanciatelo una seconda volta: è ancora `Ordine n. 1`? Grazie a chi? Ed è verde anche la sonda del punto 4?

> 🧩 **Non sai da dove partire?** Prima il test. Copiatelo in `tests/e2e/test_acquisto.py`, sotto `test_la_home_si_apre`, e sostituite i `???`:
>
> ```python
> def test_acquisto_completo(page: Page):
>     # Arrange: apro la home e faccio login
>     page.goto("/")
>     page.get_by_label("Username").fill("???")
>     page.get_by_label("???").fill("password123")
>     page.get_by_role("button", name="???").click()
>     expect(page.get_by_text("Ciao mario!")).to_be_visible()   # il login è finito davvero
>
>     # Act
>     # CSS (.scheda) perché la scheda del prodotto non ha un ruolo: il bottone dentro invece sì
>     scheda = page.locator(".scheda").filter(has_text="???")
>     scheda.get_by_role("???", name="Aggiungi").click()
>     expect(page.get_by_text("1 × Tastiera meccanica")).to_be_visible()
>     page.get_by_label("CAP").fill("???")
>     page.get_by_role("button", name="???").click()
>
>     # Assert: quello che VEDE l'utente
>     expect(page.get_by_text("???")).to_be_visible()
>     expect(page.get_by_text("Il carrello è vuoto")).to_be_visible()
> ```
>
> Poi l'HTML. In `index.html`, per ogni campo un'etichetta collegata con `for` = `id` del campo, e un vero bottone:
>
> ```html
> <label for="???">Username</label>
> <input id="username" type="text" placeholder="Username">
> ...
> <label for="cap">???</label>
> <input id="cap" type="text" placeholder="CAP">
> ...
> <button type="???" class="btn btn-primario" id="conferma-ordine">Conferma ordine</button>
> ```
>
> (Il vecchio `onclick="confermaOrdine()"` va **tolto**: il checkout lo fa partire il form.)
>
> In `app.js`, dentro `caricaCatalogo()`, il `<div>` diventa un `<button>` e il click si collega da JavaScript:
>
> ```javascript
> scheda.innerHTML = `
>   <img src="${p.immagine}">
>   <h3>${p.nome}</h3>
>   <p class="prezzo">€ ${p.prezzo.toFixed(2)}</p>
>   <button type="???" class="btn">Aggiungi</button>
> `;
> scheda.querySelector("???").addEventListener("click", () => aggiungi(p.id));
> ```
>
> E il checkout, sempre in `app.js`:
>
> ```javascript
> async function confermaOrdine(evento) {
>   evento.???();                      // la trappola: senza questa riga la pagina si ricarica
>   // ... il resto della funzione non cambia ...
> }
>
> // in fondo al file, accanto al listener del login:
> document.getElementById("form-checkout").addEventListener("???", confermaOrdine);
> ```
>
> **Trucco:** `pytest tests/e2e --headed --slowmo 500` anche con il test a metà: vedete fino a dove arriva il browser e dove si ferma. Se la pagina nel **vostro** browser non mostra le modifiche, ricaricatela con `Cmd+Shift+R` (Mac) o `Ctrl+F5` (Windows).

## Livello 2: Ingegneria (per chi va veloce; poi è nel compito)

1. **Lo scanner automatico.** Il test con i ruoli ha trovato etichette e bottoni. Ma la pagina è accessibile? Chiediamolo ad **axe-core**, uno scanner che controlla decine di regole WCAG. Create `tests/e2e/test_accessibilita.py`:

   ```python
   from axe_playwright_python.sync_playwright import Axe
   from playwright.sync_api import Page, expect

   IMPATTI_BLOCCANTI = {"critical", "serious"}


   def descrivi(violazioni):
       """Una riga per regola violata: gravità, nome della regola, quanti elementi, un esempio."""
       righe = []
       for v in violazioni:
           righe.append(f"[{v['impact']}] {v['id']} ({len(v['nodes'])} elementi) es. {v['nodes'][0]['html'][:80]}")
       return "\n".join(righe)


   def test_nessuna_violazione_grave(page: Page):
       # Arrange: la pagina va scansionata COMPLETA, cioè con il catalogo caricato
       page.goto("/")
       expect(page.get_by_role("heading", level=3)).to_have_count(4)

       # Act
       risultati = Axe().run(page)
       gravi = [v for v in risultati.response["violations"] if v["impact"] in IMPATTI_BLOCCANTI]

       # Assert
       assert gravi == [], descrivi(gravi)
   ```

   Perché prima di lanciare axe bisogna aspettare i 4 titoli del catalogo? Cosa succede se non lo fate?

2. **Correggete finché axe è verde.** Il report vi dirà:
   - `html-has-lang`: `<html lang="it">`. Senza, il lettore di schermo legge l'italiano con la pronuncia inglese;
   - `image-alt`: ogni `<img>` ha un `alt` (in `app.js`: `alt="${p.nome}"`);
   - `color-contrast`: WCAG AA chiede almeno **4,5:1** per il testo normale. Il prezzo lilla chiaro su bianco è a 2,0:1. I colori sono tutti nei "design token" in cima a `style.css` (le variabili `--...` dentro `:root`): si corregge cambiando quelle righe, non il layout. Ce n'è uno che a occhio non avreste mai notato: trovatelo nel report.

   Il Quality Gate è **zero violazioni `critical` e `serious`**. La `moderate` che resta (`page-has-heading-one`) si annota e si corregge quando si può, ma non blocca.

3. **Il Page Object Model.** Il vostro test è una lista di `page.get_by_...`. Ne scriverete altri 20: se domani il bottone "Accedi" diventa "Entra", li correggete tutti e 20? Create `tests/e2e/pagina_bottega.py` con una classe `PaginaBottega` che:
   - nel costruttore riceve `page` e definisce **tutti** i locator (`self.campo_username = page.get_by_label("Username")`);
   - espone le **azioni dell'utente** come metodi: `apri()`, `accedi(username, password)`, `aggiungi_al_carrello(nome_prodotto)`, `conferma_ordine(cap)`;
   - in `accedi()` aspetta il saluto `Ciao mario!` prima di tornare. Il click su "Accedi" ritorna **subito**, il token arriva **dopo**: l'auto-waiting aspetta gli elementi, non lo stato della vostra applicazione, e quello lo dichiarate voi.

   Poi aggiungete in `conftest.py` una fixture `bottega(page)` che restituisce `PaginaBottega(page)` e riscrivete il test:

   ```python
   def test_acquisto_completo(bottega):
       # Arrange
       bottega.apri()
       bottega.accedi("mario", "password123")
       # Act
       bottega.aggiungi_al_carrello("Tastiera meccanica")
       ...
   ```

   **Regola del POM:** nei file `test_*.py` non compare **nessun** `get_by_...`. I test dicono **cosa** fa l'utente; il Page Object sa **come** è fatta la pagina.

## Livello 3: Escalation (facoltativo)

1. **Sad path.** Due test nuovi, usando solo il Page Object: login con password sbagliata → compare "credenziali non valide" e il campo CAP **non** è visibile (`to_be_hidden()`); click su "Aggiungi" senza login → compare "Devi accedere prima di comprare". Vi serve un metodo diverso da `accedi()`, che **non** aspetti il saluto. Come lo chiamate?
2. **La tastiera.** Un test che porta il focus sul bottone "Aggiungi" del Cavo USB-C (`.focus()`), verifica con `expect(...).to_be_focused()` che l'abbia ricevuto, preme `Enter` e controlla il carrello. Poi l'esperimento: rimettete un `<div>` al posto del `<button>`, ma con `role="button"`. Quali test tornano verdi? Quale resta rosso? Cosa vi dice sui "trucchi" ARIA?
3. **Zero violazioni non vuol dire accessibile.** Lanciate axe sulla pagina **originale** (`git stash`, poi `git stash pop`): trova i bottoni-`div`? E le etichette mancanti? Scrivete in un commento perché servono **entrambi** gli strumenti. Poi scansionate anche lo stato **dopo il login** (il form del checkout prima è nascosto, e axe controlla solo ciò che è visibile).
4. **Il registratore contro di voi.** `python -m playwright codegen localhost:8000`: registrate lo stesso acquisto e scrivete in un commento **tre** motivi per cui il codice generato non passerebbe una code review.
5. **La prova vera.** VoiceOver (Mac: `Cmd+F5`) o l'Assistente vocale (Windows: `Ctrl+Win+Invio`): provate a comprare un mouse a occhi chiusi, prima e dopo le correzioni.

## Documentazione

- Playwright per Python, primi passi: https://playwright.dev/python/docs/intro
- Plugin pytest (opzioni `--headed`, `--slowmo`, fixture `page`, `base_url`): https://playwright.dev/python/docs/test-runners
- Locator e loro priorità: https://playwright.dev/python/docs/locators
- Auto-waiting: https://playwright.dev/python/docs/actionability
- Asserzioni `expect`: https://playwright.dev/python/docs/test-assertions
- Aria snapshot: https://playwright.dev/python/docs/aria-snapshots
- Codegen: https://playwright.dev/python/docs/codegen
- Page Object Model: https://playwright.dev/python/docs/pom
- axe-playwright-python: https://github.com/pamelafox/axe-playwright-python
- Regole di axe-core e gravità: https://github.com/dequelabs/axe-core/blob/develop/doc/rule-descriptions.md
- WCAG 2.1 in breve (W3C): https://www.w3.org/WAI/standards-guidelines/wcag/glance/
- Contrasto minimo (WCAG 1.4.3): https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html
- MDN, il primo principio di ARIA ("usate l'HTML nativo"): https://developer.mozilla.org/en-US/docs/Web/Accessibility/ARIA
- European Accessibility Act (Commissione europea): https://commission.europa.eu/strategy-and-policy/policies/justice-and-fundamental-rights/disability/union-equality-strategy-rights-persons-disabilities-2021-2030/european-accessibility-act_en
