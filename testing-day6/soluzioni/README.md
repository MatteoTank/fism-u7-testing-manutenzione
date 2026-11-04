# Soluzioni del Giorno 6 (parziali)

Qui trovate le soluzioni del **Lab 1** (completo) e del **Livello 1 del Lab 2**. Il resto del Lab 2 e il Lab 3 li facciamo venerdì in aula.

## Come usarle

Copiate i file di `tests/` nella cartella `tests/` della **vostra** Bottega (non sostituite i vostri: confrontateli) e lanciate `pytest` con corriere e app accesi.

## "Ma ci sono dei test rossi!"

Sì, ed è giusto così. Su La Bottega originale:

- **8 test del Lab 1 sono rossi**: sono i bug che avete trovato martedì (500 invece di 400 con il JSON rotto, 404 in HTML invece che in JSON). Un test rosso che dimostra un bug è un documento di collaudo, non un errore del test. Diventano verdi quando correggete `app.py` (è il compito).
- **`test_aggiunta_al_carrello`** passa la prima volta e diventa rosso se lanciate `pytest` una seconda volta. Chiedetevi perché prima di venerdì: è il punto di partenza del Livello 2.
