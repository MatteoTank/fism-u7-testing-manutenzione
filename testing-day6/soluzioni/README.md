# Soluzioni del Giorno 6 (Lab 1 e Lab 2 fino al Livello 2)

Qui trovate le soluzioni del **Lab 1** (completo) e del **Lab 2 fino al Livello 2** (quello che abbiamo fatto in aula martedì e venerdì). Il Livello 3 del Lab 2 è una sfida facoltativa: la sua soluzione esce più avanti. Le soluzioni del Lab 3 escono dopo la consegna del compito.

## Come usarle

Copiate i file di `tests/` nella cartella `tests/` della **vostra** Bottega (non sostituite i vostri: confrontateli) e lanciate `pytest` con corriere e app accesi.

## "Ma ci sono dei test rossi!"

Sì, ed è giusto così. Sulla Bottega **originale** sono rossi 14 test:

- **8 del Lab 1**: 500 invece di 400 con il JSON rotto, 404 in HTML invece che in JSON;
- **4 sad path del carrello**: quantità negativa, zero, stringa e campo mancante vengono accettati (`201`) o fanno esplodere il server (`500`);
- **2 login falliti**: il messaggio dice se l'utente esiste.

Un test rosso che dimostra un bug è un documento di collaudo, non un errore del test. Diventano tutti verdi con le correzioni di `app.py` (le trovate in `testing-day7/bottega_start/app.py`, cercate `[FIX G1]`).

## La fixture `stato_pulito`

È in `conftest.py`. Provate a toglierle `autouse=True` e lanciate `pytest`: `test_aggiunta_visibile_leggendo_il_carrello` diventa rosso con `assert 4 == 2`, perché un test precedente ha già messo 2 mouse nel carrello.
