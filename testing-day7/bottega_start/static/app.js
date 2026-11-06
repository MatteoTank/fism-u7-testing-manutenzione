let token = null;

async function caricaCatalogo() {
  const risposta = await fetch("/api/prodotti");
  const prodotti = await risposta.json();

  const catalogo = document.getElementById("catalogo");
  catalogo.innerHTML = "";
  for (const p of prodotti) {
    const scheda = document.createElement("div");
    scheda.className = "scheda";
    scheda.innerHTML = `
      <img src="${p.immagine}">
      <h3>${p.nome}</h3>
      <p class="prezzo">€ ${p.prezzo.toFixed(2)}</p>
      <div class="btn" onclick="aggiungi(${p.id})">Aggiungi</div>
    `;
    catalogo.appendChild(scheda);
  }
}

async function login(evento) {
  evento.preventDefault();
  const risposta = await fetch("/api/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      username: document.getElementById("username").value,
      password: document.getElementById("password").value,
    }),
  });
  const dati = await risposta.json();
  if (!risposta.ok) {
    mostraMessaggio(dati.errore, true);
    return;
  }
  token = dati.token;
  document.getElementById("form-login").hidden = true;
  const benvenuto = document.getElementById("benvenuto");
  benvenuto.textContent = `Ciao ${document.getElementById("username").value}!`;
  benvenuto.hidden = false;
  document.getElementById("form-checkout").hidden = false;
  mostraMessaggio("");
  caricaCarrello();
}

async function caricaCarrello() {
  const risposta = await fetch("/api/carrello", {
    headers: { Authorization: `Bearer ${token}` },
  });
  const dati = await risposta.json();
  const contenitore = document.getElementById("carrello");
  if (dati.righe.length === 0) {
    contenitore.innerHTML = '<p class="vuoto">Il carrello è vuoto</p>';
    return;
  }
  contenitore.innerHTML =
    "<ul>" +
    dati.righe.map((r) => `<li>${r.quantita} × ${r.nome} <span>€ ${r.subtotale.toFixed(2)}</span></li>`).join("") +
    "</ul>" +
    `<p class="totale">Totale: € ${dati.totale.toFixed(2)}</p>`;
}

async function aggiungi(prodottoId) {
  if (!token) {
    mostraMessaggio("Devi accedere prima di comprare", true);
    return;
  }
  await fetch("/api/carrello", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({ prodotto_id: prodottoId, quantita: 1 }),
  });
  caricaCarrello();
}

async function confermaOrdine() {
  const risposta = await fetch("/api/ordini", {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify({
      cap: document.getElementById("cap").value,
      codice_sconto: document.getElementById("codice-sconto").value,
    }),
  });
  const dati = await risposta.json();
  mostraMessaggio(`Ordine n. ${dati.id} confermato! Totale pagato: € ${dati.totale.toFixed(2)}`);
  caricaCarrello();
  caricaCatalogo();
}

function mostraMessaggio(testo, errore = false) {
  const box = document.getElementById("messaggio");
  box.textContent = testo;
  box.className = errore ? "errore" : "successo";
}

document.getElementById("form-login").addEventListener("submit", login);
caricaCatalogo();
