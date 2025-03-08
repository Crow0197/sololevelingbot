// URL base per le tue API
// const API_BASE =
//   "https://66624fa4-5560-4fef-96c2-224a50172da8-00-inci5z2l9nqr.picard.replit.dev";

const API_BASE = "http://localhost:8000";

// Iniezione di stile dark minimale
const style = document.createElement("style");
style.innerHTML = `
    /* Icona del widget (in basso a sinistra) */
    #sl-widget-icon {
      position: fixed;
      bottom: 20px;
      left: 20px;
      width: 50px;
      height: 50px;
      background: #444;
      color: #fff;
      border-radius: 50%;
      cursor: pointer;
      z-index: 999999;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 24px;
      box-shadow: 0 2px 6px rgba(0,0,0,0.5);
    }
    #sl-widget-icon:hover { background: #666; }

    /* Overlay della modale */
    #sl-modal-overlay {
      position: fixed;
      top: 0; left: 0; right: 0; bottom: 0;
      background: rgba(0,0,0,0.7);
      display: none;
      z-index: 1000000;
      align-items: center;
      justify-content: center;
    }

    /* Contenitore della modale */
    #sl-modal {
      background: #222;
      color: #ddd;
      width: 90%;
      max-width: 700px;
      border-radius: 8px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.8);
      font-family: sans-serif;
      overflow: hidden;
    }

    /* Header della modale */
    #sl-modal-header {
      padding: 10px 15px;
      background: #333;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    #sl-modal-header h2 { margin: 0; font-size: 18px; }
    #sl-modal-close { cursor: pointer; font-size: 20px; }

    /* Barra di navigazione per i tab */
    #sl-tab-nav {
      display: flex;
      border-bottom: 1px solid #444;
      background: #333;
    }
    .sl-tab-btn {
      flex: 1;
      padding: 10px;
      text-align: center;
      cursor: pointer;
      border: none;
      background: #333;
      color: #ccc;
      transition: background 0.3s, color 0.3s;
    }
    .sl-tab-btn.active {
      background: #222;
      color: #fff;
      font-weight: bold;
    }

    /* Contenuto dei tab */
    .sl-tab-content {
      display: none;
      padding: 15px;
    }
    .sl-tab-content.active {
      display: block;
    }

    /* Input e pulsanti */
    .sl-input {
      width: 100%;
      padding: 8px;
      margin: 5px 0;
      border: 1px solid #444;
      border-radius: 4px;
      background: #333;
      color: #fff;
    }
    .sl-btn {
      background: #555;
      color: #fff;
      border: none;
      padding: 10px;
      margin: 5px 0;
      border-radius: 4px;
      cursor: pointer;
    }
    .sl-btn:hover { background: #777; }
  `;
document.head.appendChild(style);

// Creazione dell'icona del widget
const widgetIcon = document.createElement("div");
widgetIcon.id = "sl-widget-icon";
widgetIcon.textContent = "💬";
document.body.appendChild(widgetIcon);

// Creazione della modale e dell'overlay
const modalOverlay = document.createElement("div");
modalOverlay.id = "sl-modal-overlay";
modalOverlay.innerHTML = `
    <div id="sl-modal">
      <div id="sl-modal-header">
        <h2>Solo Leveling Widget</h2>
        <span id="sl-modal-close">&times;</span>
      </div>
      <div id="sl-tab-nav"></div>
      <div id="sl-tab-container"></div>
    </div>
  `;
document.body.appendChild(modalOverlay);

// Mostra/nascondi la modale
function showModal() {
  buildTabs();
  modalOverlay.style.display = "flex";
}
function hideModal() {
  modalOverlay.style.display = "none";
}

widgetIcon.addEventListener("click", showModal);
document.getElementById("sl-modal-close").addEventListener("click", hideModal);

/**
 * buildTabs()
 * Se l'utente non è loggato -> tab Login e Register
 * Se l'utente è loggato -> tab Profile, Fight, RankUp, BossBattle, Dungeon, Complete, Logout
 */
function buildTabs() {
  const stored = localStorage.getItem("slUser");
  const user = stored ? JSON.parse(stored) : null;
  const tabNav = document.getElementById("sl-tab-nav");
  const tabContainer = document.getElementById("sl-tab-container");
  tabNav.innerHTML = "";
  tabContainer.innerHTML = "";

  if (!user) {
    // Utente NON loggato => 2 tab: Login e Register
    const tabs = [
      { id: "login", label: "Login" },
      { id: "register", label: "Register" },
    ];
    let navHTML = "";
    tabs.forEach((t, idx) => {
      navHTML += `<button class="sl-tab-btn ${idx === 0 ? "active" : ""}" data-tab="${t.id}">${t.label}</button>`;
    });
    tabNav.innerHTML = navHTML;

    let contentHTML = `
        <div class="sl-tab-content active" id="login" style="text-align: left;">
          <p><strong>Login con Username</strong></p>
          <input type="text" id="sl-login-username" class="sl-input" placeholder="Inserisci Username" />
          <button class="sl-btn" id="sl-login-btn">Login</button>
          <p style="margin-top:10px; color:#aaa;">(Se non esiste, ti avviserà di registrarti nella tab Register)</p>
        </div>

        <div class="sl-tab-content" id="register">
          <p><strong>Registrazione Utente</strong></p>
          <label class="form-label">User ID (opzionale)</label>
          <input type="text" id="sl-reg-userid" class="sl-input" placeholder="(lascia vuoto per generarlo)" />
          <label class="form-label">Username</label>
          <input type="text" id="sl-reg-username" class="sl-input" placeholder="Nome utente" />
          <button class="sl-btn" id="sl-reg-btn">Registra</button>
        </div>
      `;
    tabContainer.innerHTML = contentHTML;

    // Switch tab
    document.querySelectorAll("#sl-tab-nav .sl-tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document
          .querySelectorAll("#sl-tab-nav .sl-tab-btn")
          .forEach((b) => b.classList.remove("active"));
        document
          .querySelectorAll("#sl-tab-container .sl-tab-content")
          .forEach((c) => c.classList.remove("active"));
        btn.classList.add("active");
        const target = btn.getAttribute("data-tab");
        document.getElementById(target).classList.add("active");
      });
    });

    // Login e Register
    document
      .getElementById("sl-login-btn")
      .addEventListener("click", loginByUsername);
    document
      .getElementById("sl-reg-btn")
      .addEventListener("click", registerUser);
  } else {
    // Utente loggato => tab comandi
    const tabs = [
      { id: "profile", label: "Profile" },
      // { id: "fight", label: "Fight" },
      // { id: "rankup", label: "RankUp" },
      // { id: "bossbattle", label: "BossBattle" },
      { id: "dungeon", label: "Dungeon" },
      { id: "dungeoncomplete", label: "Complete" },
      { id: "logout", label: "Logout" },
    ];
    let navHTML = "";
    tabs.forEach((t, idx) => {
      navHTML += `<button class="sl-tab-btn ${idx === 0 ? "active" : ""}" data-tab="${t.id}">${t.label}</button>`;
    });
    tabNav.innerHTML = navHTML;

    let contentHTML = `
        <div class="sl-tab-content active" id="profile"  style="text-align: left;">
          <p>Profilo di <strong>${user.username}</strong>:</p>
          <button class="sl-btn" id="sl-profile-btn">Mostra Profilo</button>
          <div id="sl-profile-result" style="margin-top:10px;"></div>
        </div>

        <div class="sl-tab-content" id="fight">
          <p>Combatti (user_id: ${user.user_id}):</p>
          <button class="sl-btn" id="sl-fight-btn">Fight</button>
          <div id="sl-fight-result" style="margin-top:10px;"></div>
        </div>

        <div class="sl-tab-content" id="rankup">
          <p>Avanzamento di grado (user_id: ${user.user_id}):</p>
          <button class="sl-btn" id="sl-rankup-btn">RankUp</button>
          <div id="sl-rankup-result" style="margin-top:10px;"></div>
        </div>

        <div class="sl-tab-content" id="bossbattle">
          <p>Simula una battaglia contro un boss:</p>
          <button class="sl-btn" id="sl-bossbattle-btn">BossBattle</button>
          <div id="sl-bossbattle-result" style="margin-top:10px;"></div>
        </div>

        <div class="sl-tab-content" id="dungeon">
          <p>Genera un dungeon (B, A, S):</p>
          <input type="text" id="sl-dungeon-diff" class="sl-input" placeholder="B, A, S" / style="  width: 98%;">
          <button class="sl-btn" id="sl-dungeon-btn">Crea Dungeon</button>
          <div id="sl-dungeon-result" style="margin-top:10px; text-align: left;"></div>
        </div>

        <div class="sl-tab-content" id="dungeoncomplete">
          <p>Completa un dungeon (user_id: ${user.user_id}):</p>
          <input type="text" id="sl-dc-id" class="sl-input" placeholder="Dungeon ID"  style="width: 98%;"/>
          <div style="margin:5px 0;">
            <label>
              <input type="checkbox" id="sl-dc-success" />
              Successo (se non spuntato = fallimento)
            </label>
          </div>
          <button class="sl-btn" id="sl-dc-btn">Completa Dungeon</button>
          <div id="sl-dc-result" style="margin-top:10px;"></div>
        </div>

        <div class="sl-tab-content" id="logout">
          <p>Sei loggato come <strong>${user.username}</strong> (ID: ${user.user_id}). Vuoi effettuare il logout?</p>
          <button class="sl-btn" id="sl-logout-btn2">Logout</button>
        </div>
      `;
    tabContainer.innerHTML = contentHTML;

    // Tab switching
    document.querySelectorAll("#sl-tab-nav .sl-tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => {
        document
          .querySelectorAll("#sl-tab-nav .sl-tab-btn")
          .forEach((b) => b.classList.remove("active"));
        document
          .querySelectorAll("#sl-tab-container .sl-tab-content")
          .forEach((c) => c.classList.remove("active"));
        btn.classList.add("active");
        const target = btn.getAttribute("data-tab");
        document.getElementById(target).classList.add("active");
      });
    });

    // Event listener per i comandi
    document
      .getElementById("sl-profile-btn")
      .addEventListener("click", showProfile);
    document
      .getElementById("sl-fight-btn")
      .addEventListener("click", fightBoss);
    document.getElementById("sl-rankup-btn").addEventListener("click", rankUp);
    document
      .getElementById("sl-bossbattle-btn")
      .addEventListener("click", bossBattle);
    document
      .getElementById("sl-dungeon-btn")
      .addEventListener("click", createDungeon);
    document
      .getElementById("sl-dc-btn")
      .addEventListener("click", completeDungeon);
    document
      .getElementById("sl-logout-btn2")
      .addEventListener("click", logoutUser);
  }
}

/**
 * Funzione generica per chiamare l'API
 */
async function callAPI(endpoint, method = "GET", body = null) {
  try {
    const options = { method };
    if (body) {
      options.headers = { "Content-Type": "application/json" };
      options.body = JSON.stringify(body);
    }
    const res = await fetch(API_BASE + endpoint, options);
    if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
    return await res.json();
  } catch (err) {
    return { error: err.message };
  }
}

/**
 * Login con username
 * Tenta /profile/{username}. Se esiste => salva localStorage. Se 404 => avvisa di registrarsi.
 */
async function loginByUsername() {
  const uname = document.getElementById("sl-login-username").value.trim();
  if (!uname) {
    alert("Inserisci un nome utente");
    return;
  }

  const check = await callAPI(`/profile/${uname}`, "GET");
  if (check.error) {
    alert(
      "Utente non trovato o errore. Prova a registrarti nella tab 'Register'.",
    );
    return;
  }
  if (check.username && check.user_id) {
    // Salviamo in localStorage
    localStorage.setItem(
      "slUser",
      JSON.stringify({ username: check.username, user_id: check.user_id }),
    );
    alert("Login riuscito: " + check.username);
    buildTabs();
  }
}

/**
 * Registrazione utente
 */
async function registerUser() {
  const userId = document.getElementById("sl-reg-userid").value.trim();
  const uname = document.getElementById("sl-reg-username").value.trim();
  if (!uname) {
    alert("Inserisci username");
    return;
  }

  // Se l'utente non inserisce userId, lo generiamo
  const finalId = userId || Date.now().toString();
  const body = { user_id: finalId, username: uname };
  const resp = await callAPI("/register", "POST", body);
  if (resp.error) {
    alert("Errore: " + resp.error);
    return;
  }
  if (resp.message && resp.user_id) {
    alert(resp.message);
    localStorage.setItem(
      "slUser",
      JSON.stringify({ username: uname, user_id: resp.user_id }),
    );
    buildTabs();
  }
}

/**
 * Mostra il profilo
 * Usa /profile/{username}, restituisce un oggetto con i dati
 */
async function showProfile() {
  const user = JSON.parse(localStorage.getItem("slUser"));
  const resultDiv = document.getElementById("sl-profile-result");
  resultDiv.innerHTML = "Caricamento...";

  const resp = await callAPI(`/profile/${user.username}`, "GET");
  if (resp.username) {
    // Costruiamo l'HTML includendo i nuovi campi
    const inventoryHtml = buildInventoryHtml(resp.inventory);

    resultDiv.innerHTML = `
      <div style="border:1px solid #ccc; padding:15px; border-radius:5px; background:#333; color:#fff; height:50vh; overflow-y:auto;">
        <h3 style="margin-top:0;">${resp.username} <small style="font-size:14px;">(ID: ${resp.user_id})</small></h3>
        <ul style="list-style:none; padding:0;">
          <li><strong>Grado salvato:</strong> ${resp.rank}</li>
          <li><strong>Grado calcolato:</strong> ${resp.calculated_rank}</li>
          <li><strong>Level:</strong> ${resp.level}</li>
          <li><strong>EXP:</strong> ${resp.exp} (Mancano ${resp.exp_needed_level} EXP per il prossimo livello)</li>
          <li><strong>EXP per salire di grado:</strong> ${resp.exp_needed_rank}</li>
          <li><strong>Soldi:</strong> ${resp.money}</li>
          <li><strong>Dungeon completati:</strong> ${resp.dungeons_completed}</li>
        </ul>
        <h4>Inventario</h4>
        ${inventoryHtml}
      </div>
    `;
  } else if (resp.error) {
    resultDiv.innerHTML = `<div style="color:red;">Errore: ${resp.error}</div>`;
  } else {
    resultDiv.innerHTML = `<pre>${JSON.stringify(resp, null, 2)}</pre>`;
  }
}

/**
 * Fight
 */
async function fightBoss() {
  const user = JSON.parse(localStorage.getItem("slUser"));
  const resultDiv = document.getElementById("sl-fight-result");
  resultDiv.innerHTML = "Caricamento...";

  const body = { user_id: user.user_id };
  const resp = await callAPI("/fight", "POST", body);
  if (resp.message) {
    resultDiv.innerHTML = resp.message;
  } else if (resp.error) {
    resultDiv.innerHTML = `Errore: ${resp.error}`;
  } else {
    resultDiv.innerHTML = `<pre>${JSON.stringify(resp, null, 2)}</pre>`;
  }
}

/**
 * RankUp
 */
async function rankUp() {
  const user = JSON.parse(localStorage.getItem("slUser"));
  const resultDiv = document.getElementById("sl-rankup-result");
  resultDiv.innerHTML = "Caricamento...";

  const body = { user_id: user.user_id };
  const resp = await callAPI("/rankup", "POST", body);
  if (resp.message) {
    resultDiv.innerHTML = resp.message;
  } else if (resp.error) {
    resultDiv.innerHTML = `Errore: ${resp.error}`;
  } else {
    resultDiv.innerHTML = `<pre>${JSON.stringify(resp, null, 2)}</pre>`;
  }
}

/**
 * BossBattle
 */
async function bossBattle() {
  const resultDiv = document.getElementById("sl-bossbattle-result");
  resultDiv.innerHTML = "Caricamento...";

  const resp = await callAPI("/bossbattle", "GET");
  if (resp.error) {
    resultDiv.innerHTML = `Errore: ${resp.error}`;
    return;
  }
  // Se abbiamo un bossbattle_html
  if (resp.bossbattle_html) {
    let html = "";
    if (resp.avatar_url) {
      html += `<img src="${resp.avatar_url}" style="max-width:100%; margin-bottom:10px;" alt="Boss Image">`;
    }
    html += resp.bossbattle_html;
    resultDiv.innerHTML = html;
  } else {
    // fallback
    let html = "";
    if (resp.avatar_url) {
      html += `<img src="${resp.avatar_url}" style="max-width:100%; margin-bottom:10px;" alt="Boss Image">`;
    }
    if (resp.messages) {
      html += `<pre>${resp.messages.join("\n")}</pre>`;
    }
    resultDiv.innerHTML = html;
  }
}

/**
 * Crea un dungeon
 */
async function createDungeon() {
  const user = JSON.parse(localStorage.getItem("slUser"));
  const diffVal = document
    .getElementById("sl-dungeon-diff")
    .value.toUpperCase();
  const resultDiv = document.getElementById("sl-dungeon-result");
  if (!diffVal) {
    alert("Inserisci la difficoltà (B, A, S)");
    return;
  }

  resultDiv.innerHTML = "Caricamento...";
  const body = { difficulty: diffVal };
  const resp = await callAPI("/dungeon", "POST", body);
  if (resp.error) {
    resultDiv.innerHTML = `Errore: ${resp.error}`;
    return;
  }
  const dungeon = resp.dungeon || resp;
  resultDiv.innerHTML = createDungeonCard(dungeon);
}

/**
 * Completamento dungeon con checkbox per successo/fallimento
 */
async function completeDungeon() {
  const user = JSON.parse(localStorage.getItem("slUser"));
  const dungeonId = document.getElementById("sl-dc-id").value.trim();
  const successChecked = document.getElementById("sl-dc-success").checked;
  const resultDiv = document.getElementById("sl-dc-result");

  if (!dungeonId) {
    alert("Inserisci il Dungeon ID");
    return;
  }

  // Se checkbox spuntata => outcome = "successo", altrimenti "fallimento"
  const outcome = successChecked ? "successo" : "fallimento";

  resultDiv.innerHTML = "Caricamento...";
  const body = {
    dungeon_id: dungeonId,
    outcome: outcome,
    user_id: Number(user.user_id),
  };
  const resp = await callAPI("/dungeon/complete", "POST", body);
  if (resp.error) {
    resultDiv.innerHTML = `Errore: ${resp.error}`;
  } else if (resp.message) {
    resultDiv.innerHTML = `<pre>${resp.message}</pre>`;
  } else {
    resultDiv.innerHTML = `<pre>${JSON.stringify(resp, null, 2)}</pre>`;
  }
}

/**
 * Funzione per creare una card HTML di un dungeon
 */
function createDungeonCard(dungeon) {
  if (!dungeon.id) return "Dungeon non valido";
  let encountersHTML = "";
  if (dungeon.encounters && dungeon.encounters.length > 0) {
    dungeon.encounters.forEach((enc) => {
      if (enc.nemico && enc.nemico.nome) {
        encountersHTML += `<li>${enc.tipo === "boss" ? "Boss Principale" : "Miniboss"}: ${enc.nemico.nome}</li>`;
      }
    });
  }
  return `
      <div style="border:1px solid #444; padding:10px; border-radius:4px; background:#333; color:#fff;">
        <p><strong>ID:</strong> ${dungeon.id}</p>
        <p><strong>Difficoltà:</strong> ${dungeon.difficulty}</p>
        <p><strong>Incontri:</strong></p>
        <ul>${encountersHTML}</ul>
        <p><strong>Premio:</strong> ${dungeon.money} soldi, ${dungeon.exp_reward} EXP</p>
      </div>
    `;
}

/**
 * Logout
 */
function logoutUser() {
  localStorage.removeItem("slUser");
  alert("Logout effettuato.");
  buildTabs();
}

function buildInventoryHtml(items) {
  // Se non ci sono item, restituisce "Vuoto"
  if (!items || items.length === 0) {
    return "Vuoto";
  }

  // Raggruppa gli item per 'type'
  const grouped = {};
  items.forEach((item) => {
    const t = item.type || "Sconosciuto";
    if (!grouped[t]) {
      grouped[t] = [];
    }
    grouped[t].push(item);
  });

  let html = "";
  // Per ogni tipologia, crea un blocco collapsible con <details>
  for (const type in grouped) {
    // Calcola il colore in base al grado migliore (o in base al primo item)
    // Puoi decidere come definire il colore: qui usiamo il grado del primo item
    const grade = grouped[type][0].grade;
    const color = gradeColors[grade] || "#fff";
    html += `<details style="margin-bottom:8px;">`;
    // Colora il titolo della sezione
    html += `<summary style="color: ${color}; font-weight: bold;">${type} (${grouped[type].length})</summary>`;
    html += `<ul style="list-style:none; padding-left:1em;">`;
    grouped[type].forEach((obj) => {
      const name = obj.name || "Senza Nome";
      const grade = obj.grade || "?";
      const desc = obj.description || "";
      const eff = obj.effect || "";
      const ability = obj.ability || "";
      const color = gradeColors[grade] || "#fff"; // default bianco se non definito
      html += `<li style="margin-bottom:15px; border: 2px solid white; padding: 5px">`;
      html += `<b style="color: ${color};">${name}</b> (Grado: ${grade})<br/>`;
      html += `<i>${desc}</i><br/>`;
      html += `Effetto: ${eff}<br/>`;
      html += `Abilità: ${ability}`;
      html += `</li>`;
    });

    html += `</ul>`;
    html += `</details>`;
  }
  return html;
}

const gradeColors = {
  E: "#888", // grigio
  D: "orange", // blu
  C: "#0a0", // verde
  B: "#ff0", // giallo
  A: "#f80", // arancione
  S: "#f00", // rosso
};
