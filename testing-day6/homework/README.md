# Homework: Il primo rapporto di collaudo

## Contesto

Avete passato la giornata a dimostrare che La Bottega **non** rispetta il suo contratto. Ora siete voi i responsabili della correzione. Prima di venerdì, però, c'è una cosa da fare per la prossima lezione, ed è **obbligatoria per tutti**.

## Livello 0: Preparazione per venerdì (OBBLIGATORIO)

Venerdì faremo test sull'interfaccia grafica con un browser comandato da Python. Serve scaricare il browser: circa 150 MB da scaricare (quasi 600 MB una volta installato), troppo per la rete dell'aula se lo fate tutti insieme.

Con il venv della Bottega attivo:

```bash
pip install pytest-playwright
python -m playwright install chromium
```

Verifica: `python -m playwright --version` stampa una versione. Se ricevete errori, mandateli **prima** di venerdì, non durante la lezione.

## Livello 1: Sopravvivenza (obbligatorio per tutti)

1. Completate i test dei Lab 1, 2 e 3 fino al Livello 2 compreso.
2. Lanciate `pytest`. Molti test saranno **rossi**: è corretto, sono i bug della Bottega.
3. Create il file `BUG_REPORT.md` nella radice del progetto, con una sezione per ogni bug trovato:

   ```markdown
   ## BUG-001: <titolo breve>
   - **Endpoint:** POST /api/...
   - **Passi per riprodurlo:** ...
   - **Atteso (contratto):** 400 con {"errore": ...}
   - **Ottenuto:** 500 con pagina HTML
   - **Gravità:** Bloccante / Alta / Media / Bassa  (e perché)
   - **Test che lo dimostra:** tests/test_xxx.py::test_yyy
   ```

## Livello 2: Ingegneria (standard)

Correggete `app.py` e `spedizioni.py` finché **tutti** i test sono verdi, compreso `pytest -m chaos` con il corriere spento.

Vincoli architetturali (Quality Gate):
- **Vietato** riempire ogni endpoint di `try/except` copiati e incollati. La lettura e la validazione del JSON vanno in **un solo** punto riutilizzabile.
- **Vietato** modificare i test per farli passare. Se un test vi sembra sbagliato, rileggete il contratto. Se il contratto è ambiguo, scrivetelo nel bug report.
- Un commit per ogni bug corretto, con un messaggio che cita il codice del bug (`fix: BUG-003 quantità negativa nel carrello`).

## Livello 3: Escalation (per chi vuole l'eccellenza)

**La pipeline.** Recuperate il workflow GitHub Actions del semestre 1 e adattatelo alla Bottega. Il problema nuovo: i test black box hanno bisogno di un server **acceso** dentro il runner. Indizi:
- in un passaggio `run:` potete avviare un processo in background con `python corriere.py &`;
- prima di lanciare `pytest` serve aspettare che il server risponda (`sleep 3` è la versione rozza; un ciclo con `curl` è quella professionale).

Obiettivo: pallino verde su GitHub con tutti i test, chaos esclusi.

---

## Istruzioni per la consegna

1. Create un repository **privato** su GitHub con il progetto. Controllate che `venv/` **non** sia nel repo (c'è già il `.gitignore`).
2. Aggiungete il docente come collaboratore.
3. Mandate il link del repository a `angeligiovanni21@gmail.com` entro le 23:59 di giovedì.
