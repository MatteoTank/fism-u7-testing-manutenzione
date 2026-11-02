# SETUP — Giorno 6: il vostro primo giorno alla Bottega

Da oggi non lavorate più su esercizi isolati. Siete stati assunti in un'azienda che ha un e-commerce, **La Bottega**, e il team precedente se n'è andato. Il codice "funziona", dicono. Per il resto del corso il vostro compito è uno solo: **dimostrarlo, oppure dimostrare il contrario.**

> 🔁 **Arrugginiti sul semestre 1?** Venv, pytest, mock, Git, CI, subprocess: tutto in [`RECAP_SEMESTRE_1.md`](../RECAP_SEMESTRE_1.md), con le domande frequenti.
>
> 📖 **Prima di iniziare.** Oggi useremo parole come *client*, *server*, *porta*, *localhost*, *processo*. Se anche una sola non vi è chiara al 100%, leggete la **Parte 1** di [`CONCETTI_BASE.md`](../CONCETTI_BASE.md) (10 minuti, con l'analogia del ristorante). Non è tempo perso: è il tempo che risparmierete dopo.

## 1. Prendete il codice e mettetelo sotto Git

Copiate la cartella `bottega/` del repository del corso in una posizione vostra, **fuori** dalla cartella del corso.

```bash
cd bottega
git init
git add .
git commit -m "chore: codice ereditato dal team precedente"
```

> Il primo commit è la fotografia di ciò che avete ricevuto. Ogni modifica futura si potrà confrontare con questo punto zero.

## 2. Il recinto (virtual environment)

```bash
python -m venv venv

# Mac/Linux
source venv/bin/activate
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## 3. Accendete il sistema: servono DUE terminali

Il sistema è **distribuito**, quindi ci sono due processi separati che parlano tra loro via HTTP. In ogni terminale, prima di tutto, attivate il venv.

> 📖 Perché due terminali? Ogni server è un **processo** che resta acceso e "occupa" il suo terminale finché non premete CTRL+C. Due server = due terminali, più un terzo per i vostri comandi. Vedi [Processo](../CONCETTI_BASE.md#processo) e [Porta](../CONCETTI_BASE.md#porta).

| Terminale | Comando | Chi è |
|-----------|---------|-------|
| 1 | `python corriere.py` | SpediVeloce, il corriere esterno (NON è nostro) |
| 2 | `python app.py` | La Bottega, il nostro backend |

## 4. Verifica

1. Aprite http://localhost:8000 nel browser, entrate con `mario` / `password123` e fate un ordine completo.
2. Aprite un **terzo** terminale (con il venv attivo) e lanciate:

```bash
pytest
```

Dovete vedere `1 passed`. Se vedete `ConnectionError`, il server del terminale 2 è spento.

## 5. Leggete il contratto

Aprite `bottega/README.md`. È la specifica concordata con il cliente. **Da adesso, ogni volta che il codice non fa quello che dice il README, avete trovato un bug.**

## Problemi frequenti

| Sintomo | Causa | Soluzione |
|---------|-------|-----------|
| `Address already in use` | Un altro processo occupa la porta | Chiudete l'altro terminale, oppure trovate e uccidete il processo |
| `ModuleNotFoundError: flask` | Il venv non è attivo in **quel** terminale | Attivatelo: ogni terminale ha il suo |
| `ConnectionError` nei test | Il server è spento | Terminale 2: `python app.py` |
| PowerShell blocca `Activate.ps1` | Execution policy | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
