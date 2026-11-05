# calcolo preventivo ordine
# scritto da Gianni 2019 - NON TOCCARE funziona!!!
# modificato 2021 per black friday
# modificato 2022 sardegna (chiesto da commerciale)
import datetime

SCONTI_USATI = []


def calcola_totale(r, t, c, cap, sped):
    # r = righe, t = tipo cliente, c = codice, sped = spedizione
    tot = 0
    for x in r:
        if x["quantita"] > 0:
            if x["prezzo"] > 0:
                tot = tot + x["prezzo"] * x["quantita"]
    print("DEBUG tot", tot)
    if t == "vip":
        if tot > 100:
            tot = tot - tot * 0.15
        else:
            tot = tot - tot * 0.05
    else:
        if t == "nuovo":
            if c == "BENVENUTO10":
                if c not in SCONTI_USATI:
                    tot = tot - 10
                    SCONTI_USATI.append(c)
        else:
            if c == "BENVENUTO10":
                pass
    if c == "BLACKFRIDAY":
        oggi = datetime.date.today()
        if oggi.month == 11:
            if oggi.day >= 24 and oggi.day <= 30:
                tot = tot * 0.8
    if tot < 0:
        tot = 0
    if cap[0:2] == "07" or cap[0:2] == "08" or cap[0:2] == "09":
        sped = sped + 5
    else:
        if cap[0:1] == "9":
            if int(cap[0:2]) >= 90 and int(cap[0:2]) <= 98:
                sped = sped + 5
    if tot > 49.99:
        sped = 0
    print("DEBUG sped", sped)
    tot = tot + sped
    tot = round(tot, 2)
    return tot
