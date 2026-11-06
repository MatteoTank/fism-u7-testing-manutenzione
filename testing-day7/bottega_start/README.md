# La Bottega — Contratto delle API (v1.0)

> Questo documento è la **specifica** concordata con il cliente.
> Il codice che avete ereditato *dovrebbe* rispettarla. Il vostro lavoro è dimostrare se lo fa davvero.
> Quando codice e contratto non sono d'accordo, **ha ragione il contratto**: quello è un bug.

## Architettura

```
 Browser / test ──HTTP──▶  La Bottega (nostra)  ──HTTP──▶  SpediVeloce (corriere esterno)
                          localhost:8000                    localhost:8001
                          app.py                            corriere.py  (NON nostro, non si tocca)
```

## Avvio (due terminali, entrambi con il venv attivo)

```bash
# Terminale 1 — il fornitore esterno
python corriere.py

# Terminale 2 — il nostro backend
python app.py
```

Il frontend è su http://localhost:8000. Gli utenti di prova sono:

| username | password      | tipo cliente |
|----------|---------------|--------------|
| mario    | password123   | nuovo        |
| giulia   | vip2026       | vip          |

I dati stanno in memoria: **a ogni riavvio del server si azzera tutto**.

---

## Regole generali (valgono per TUTTI gli endpoint)

1. **Ogni risposta è JSON**, errori compresi (`Content-Type: application/json`).
2. Ogni risposta di errore ha la forma `{"errore": "<messaggio leggibile>"}`.
3. Il server **non risponde mai 500** a causa dell'input del client. Un input sbagliato è colpa del client → `400`.
4. Gli endpoint protetti richiedono l'header `Authorization: Bearer <token>`. Se manca o non è valido → `401`.

| Status | Significato nel nostro contratto |
|--------|----------------------------------|
| 200 | OK, lettura riuscita |
| 201 | Risorsa creata (aggiunta al carrello, ordine) |
| 400 | Il client ha mandato dati malformati o non validi |
| 401 | Non autenticato |
| 404 | Risorsa inesistente |
| 409 | Conflitto con lo stato del sistema (es. stock insufficiente) |
| 503 | Un servizio esterno da cui dipendiamo non risponde |

---

## Endpoint

### `GET /api/health`
Stato del servizio. → `200` `{"status": "ok", "ambiente": "sviluppo"}`

### `GET /api/prodotti`
→ `200` lista di prodotti. Ogni prodotto ha **esattamente** questo schema:

| campo     | tipo    | note |
|-----------|---------|------|
| id        | intero  | |
| nome      | stringa | non vuota |
| prezzo    | numero  | > 0 |
| stock     | intero  | ≥ 0 |
| peso      | numero  | kg, > 0 |
| immagine  | stringa | URL relativo |

### `GET /api/prodotti/<id>`
→ `200` il prodotto · `404` se non esiste (anche se `<id>` non è un numero).

### `POST /api/login`
Body: `{"username": "...", "password": "..."}`
→ `200` `{"token": "...", "tipo": "nuovo" | "vip"}`
→ `401` `{"errore": "credenziali non valide"}`. **Per sicurezza il messaggio è identico** sia per un utente inesistente sia per una password errata.
→ `400` se il body non è JSON valido o mancano dei campi.

### `GET /api/carrello` 🔒
→ `200` `{"righe": [{"prodotto_id", "nome", "prezzo", "quantita", "subtotale"}], "totale": numero}`

### `POST /api/carrello` 🔒
Body: `{"prodotto_id": intero, "quantita": intero}`
- `quantita` deve essere un **intero ≥ 1**
- → `201` `{"prodotto_id": ..., "quantita": <quantità totale nel carrello>}`
- → `400` body malformato, campi mancanti, tipi sbagliati, quantità ≤ 0
- → `404` prodotto inesistente
- → `409` quantità richiesta superiore allo stock

### `POST /api/ordini` 🔒 (checkout)
Body: `{"cap": "50100", "codice_sconto": "BENVENUTO10"}` (`codice_sconto` è facoltativo)
- Calcola il totale (sconti + spedizione chiesta a SpediVeloce), scala lo stock e svuota il carrello.
- → `201` `{"id": intero, "utente": "...", "totale": numero}`
- → `400` carrello vuoto o body non valido
- → `503` `{"errore": "servizio spedizioni non disponibile"}` se SpediVeloce non risponde **entro 3 secondi** o risponde con un errore

### `POST /api/reset`
Riporta i dati allo stato iniziale. **Esiste solo per i test automatici.** In produzione → `403`.

---

## Servizio esterno: SpediVeloce

`GET http://localhost:8001/tariffa?cap=50100&peso=1.5` → `200` `{"costo": 4.9}`

Non è nostro e non possiamo modificarlo. Possiamo solo chiamarlo… e sperare.
