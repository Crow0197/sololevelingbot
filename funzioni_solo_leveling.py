import json
import os
import random
import uuid
from collections import defaultdict

# Percorsi dei file
USERS_FILE = "users.json"
DUNGEONS_FILE = "dungeons.json"
BOSS_LIST_FILE = "data/boss_list.json"
ITEMS_FILE = "data/itemsList.json"  # File contenente i drop

# Costanti
RANKS = ["E", "D", "C", "B", "A", "S"]
EXP_THRESHOLDS = {
    "E": 500, "D": 1000, "C": 2000, "B": 4000, "A": 8000, "S": float("inf")
}

# Configurazione per i talenti/effetti (puoi personalizzarla ulteriormente)
GRADE_CONFIG = {
    "Comune": {"talenti": 1, "effetti": 1},
    "Raro": {"talenti": 2, "effetti": 2},
    "Epico": {"talenti": None, "effetti": None},
    "Leggendario": {"talenti": None, "effetti": None}
}

GRADE_TOTAL = {
    "Comune": 2500,
    "Raro": 3000,
    "Epico": 3500,
    "Leggendario": 4000
}

# -------------------- UTENTI --------------------

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=4)

def register_user(user_id, username):
    """
    Registra un utente con user_id e username.
    Ritorna una tupla (message, user_id).
    """
    users = load_users()
    if user_id in users:
        return ("Sei già registrato! Usa /profile per vedere il tuo stato.", user_id)
    users[user_id] = {
        "username": username,
        "rank": "E",
        "exp": 0,
        "money": 0,
        "inventory": [],
        "dungeons_completed": 0
    }
    save_users(users)
    msg = f"Benvenuto {username}! Ora sei un Hunter di grado E."
    return (msg, user_id)

def get_user_profile(user_id):
    users = load_users()
    if user_id not in users:
        return None
    
    user = users[user_id]
    exp_total = user["exp"]
    
    # Calcola i parametri desiderati
    level = calculate_level(exp_total)
    exp_needed_level = exp_for_next_level(exp_total)
    calculated_rank = calculate_rank(exp_total)
    exp_needed_rank = exp_for_next_rank(exp_total)
    
    # Aggiorna il record utente con il grado calcolato
    user["rank"] = calculated_rank
    # Se vuoi, puoi anche salvare il level in user["level"] (opzionale):
    user["level"] = level
    
    # Salva i dati aggiornati
    save_users(users)
    
    return {
        "username": user["username"],
        "user_id": user_id,
        # rank ora è il nuovo rank salvato
        "rank": user["rank"],  
        "calculated_rank": calculated_rank,
        "level": level,
        "exp": exp_total,
        # Puoi eventualmente mantenere exp_threshold se ti serve
        "exp_threshold": EXP_THRESHOLDS.get(user["rank"], "N/A"),
        "exp_needed_level": exp_needed_level,
        "exp_needed_rank": exp_needed_rank,
        "money": user.get("money", 0),
        "inventory": user.get("inventory", []),
        "dungeons_completed": user.get("dungeons_completed", 0)
    }



# -------------------- COMBATTIMENTO E RANK UP --------------------

def fight_boss(user_id):
    """
    Simula un combattimento contro un boss: aggiunge EXP all'utente.
    """
    boss = get_predefined_boss()
    if boss is None:
        return "Nessun boss disponibile."
    users = load_users()
    if user_id not in users:
        return "Utente non registrato."
    users[user_id]["exp"] += boss["exp"]
    save_users(users)
    return f"Hai sconfitto {boss['nome']} e guadagnato {boss['exp']} EXP."

def rank_up_user(user_id):
    """
    Se l'utente ha EXP sufficiente, aumenta il grado.
    """
    users = load_users()
    if user_id not in users:
        return "Utente non registrato."
    user = users[user_id]
    current_rank = user["rank"]
    if current_rank == "S":
        return "Hai già raggiunto il grado massimo!"
    next_rank = RANKS[RANKS.index(current_rank) + 1]
    required_exp = EXP_THRESHOLDS[current_rank]
    if user["exp"] >= required_exp:
        user["rank"] = next_rank
        save_users(users)
        return f"Congratulazioni! Sei avanzato a {next_rank}!"
    else:
        return f"Ti servono almeno {required_exp - user['exp']} EXP per salire di grado."

# -------------------- BOSS E BOSS BATTLE --------------------

def load_boss_list():
    if not os.path.exists(BOSS_LIST_FILE):
        return []
    with open(BOSS_LIST_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("bosses", [])

def get_predefined_boss():
    """
    Seleziona casualmente un boss dalla lista e genera le sue statistiche.
    """
    bosses = load_boss_list()
    if not bosses:
        return None
    boss_template = random.choice(bosses)
    hp = boss_template["hp"]
    atk = boss_template["atk"]
    defense = boss_template["def"]
    ctk = boss_template["ctk"]
    sup = boss_template["sup"]
    exp = boss_template.get("exp", GRADE_TOTAL.get(boss_template["grado"], 2500) - (hp + atk + defense + ctk + sup))
    config = GRADE_CONFIG.get(boss_template["grado"], {"talenti": None, "effetti": None})
    talenti_list = boss_template.get("talenti", [])
    if config["talenti"] is None or config["talenti"] >= len(talenti_list):
        talenti = talenti_list
    else:
        talenti = random.sample(talenti_list, config["talenti"])
    effetti_list = boss_template.get("effetti", [])
    if config["effetti"] is None or config["effetti"] >= len(effetti_list):
        effetti = effetti_list
    else:
        effetti = random.sample(effetti_list, config["effetti"])
    boss_generated = {
        "nome": boss_template["nome"],
        "grado": boss_template["grado"],
        "hp": hp,
        "atk": atk,
        "def": defense,
        "ctk": ctk,
        "sup": sup,
        "exp": exp,
        "talenti": talenti,
        "effetti": effetti,
        "drop": boss_template.get("drop", []),
        "storia": boss_template["storia"],
        "avatar_url": boss_template["avatar_url"]
    }
    return boss_generated

def simulate_boss_battle_messages():
    """
    Simula una battaglia in 5 turni contro un boss.
    Ritorna un array di messaggi e l'URL dell'immagine del boss.
    """
    boss = get_predefined_boss()
    if boss is None:
        return None, None

    boss_name = boss["nome"]
    grade = boss["grado"]
    atk = boss["atk"]
    defense = boss["def"]
    ctk = boss["ctk"]
    sup = boss["sup"]
    hp = boss["hp"]
    exp = boss["exp"]

    messages = []
    header = f"Inizio battaglia contro {boss_name} (Grado: {grade})\nStatistiche: ATK {atk} | DEF {defense} | CTK {ctk} | SUP {sup} | HP {hp} | EXP {exp}\n----------------------------------------"
    messages.append(header)

    sup_talents = [t for t in boss["talenti"] if t["type"] == "sup"]
    def_talents = [t for t in boss["talenti"] if t["type"] == "def"]
    atk_talents = [t for t in boss["talenti"] if t["type"] == "atk"]

    def get_status_desc(status_name):
        for eff in boss["effetti"]:
            if eff["nome"] == status_name:
                return eff["descrizione"]
        return ""

    def do_action(action_type):
        if action_type == "sup":
            if sup_talents:
                chosen = random.choice(sup_talents)
                status_name = chosen["status_applicato"]
                status_desc = get_status_desc(status_name)
                return f"{boss_name} usa {chosen['nome']} (SUP) - Recupera {sup} HP. Status: {status_name} ({status_desc})"
            else:
                return f"{boss_name} si cura di {sup} HP."
        elif action_type == "def":
            if def_talents:
                chosen = random.choice(def_talents)
                status_name = chosen["status_applicato"]
                status_desc = get_status_desc(status_name)
                return f"{boss_name} usa {chosen['nome']} (Difesa) - Incrementa difesa di {sup} punti. Status: {status_name} ({status_desc})"
            else:
                return f"{boss_name} incrementa la difesa di {sup} punti."
        else:  # "atk"
            if atk_talents:
                chosen = random.choice(atk_talents)
                status_name = chosen["status_applicato"]
                status_desc = get_status_desc(status_name)
                return f"{boss_name} usa {chosen['nome']} (Attacco) - Infligge 500 danni extra. Status: {status_name} ({status_desc})"
            else:
                return f"{boss_name} attacca infliggendo 500 danni."

    def maybe_counter():
        if random.random() < 0.3:
            return f"Contrattacco (CTK: {ctk}) - Infligge 500 danni!"
        return ""

    for turn in range(1, 6):
        turn_msg = f"TURNO {turn}\n"
        turn_msg += "Fase Difensiva:\n"
        turn_msg += do_action("sup") + "\n" + maybe_counter() + "\n"
        turn_msg += do_action("def") + "\n" + maybe_counter() + "\n"
        turn_msg += "Fase Offensiva:\n"
        turn_msg += do_action("sup") + "\n" + maybe_counter() + "\n"
        turn_msg += do_action("atk") + "\n" + maybe_counter() + "\n"
        turn_msg += "----------------------------------------"
        messages.append(turn_msg)

    messages.append("Battaglia terminata!")
    html_content = '<div style="max-height:400px; overflow-y:auto;">'
    for line in messages:
        html_content += f"<p>{line}</p>"
    html_content += "</div>"

    return messages, boss["avatar_url"]

# -------------------- DUNGEON E DROP --------------------

def load_dungeons():
    if not os.path.exists(DUNGEONS_FILE):
        return {}
    with open(DUNGEONS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_dungeons(dungeons):
    with open(DUNGEONS_FILE, "w", encoding="utf-8") as f:
        json.dump(dungeons, f, indent=4)

def load_items():
    if not os.path.exists(ITEMS_FILE):
        return []
    with open(ITEMS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("items", [])

def get_random_drops(count=1, user_grade=None):
    """
    Restituisce una lista di 'count' item casuali.
    Se user_grade è uno tra "E", "D", "C", "B", "A", "S", applica una distribuzione:
      - E: sempre "E"
      - D: 80% D, 20% E
      - C: 70% C, 20% D, 10% E
      - B: 50% da ["E", "D", "C"] uniformemente, 40% B, 10% A
      - A: 40% da ["E", "D", "C", "B"], 50% A, 10% S
      - S: 90% S, 10% A
    Se non ci sono item del grado desiderato, ritorna un item casuale dall'intera lista.
    """
    all_items = load_items()
    if not all_items:
        print("[DEBUG] Nessun item disponibile in itemsList.json")
        return []

    # Definizione dei "chooser" per ciascun grado:
    def choose_grade_E():
        return "E"

    def choose_grade_D():
        r = random.random()
        return "D" if r < 0.8 else "E"

    def choose_grade_C():
        r = random.random()
        if r < 0.7:
            return "C"
        elif r < 0.9:
            return "D"
        else:
            return "E"

    def choose_grade_B():
        r = random.random()
        if r < 0.5:
            return random.choice(["E", "D", "C"])
        elif r < 0.9:
            return "B"
        else:
            return "A"

    def choose_grade_A():
        r = random.random()
        if r < 0.4:
            return random.choice(["E", "D", "C", "B"])
        elif r < 0.9:
            return "A"
        else:
            return "S"

    def choose_grade_S():
        r = random.random()
        return "S" if r < 0.9 else "A"

    grade_chooser = {
        "E": choose_grade_E,
        "D": choose_grade_D,
        "C": choose_grade_C,
        "B": choose_grade_B,
        "A": choose_grade_A,
        "S": choose_grade_S
    }

    if user_grade in grade_chooser:
        chosen_items = []
        for _ in range(count):
            target_grade = grade_chooser[user_grade]()
            filtered = [item for item in all_items if item.get("grade") == target_grade]
            if filtered:
                chosen_items.append(random.choice(filtered))
            else:
                chosen_items.append(random.choice(all_items))
        return chosen_items
    else:
        return random.choices(all_items, k=count)


def generate_miniboss():
    boss = get_predefined_boss()
    if boss is None:
        return None
    for stat in ["hp", "atk", "def", "ctk", "sup", "exp"]:
        boss[stat] = int(boss[stat] * 0.7)
    boss["nome"] = "Miniboss: " + boss["nome"]
    return boss

def generate_dungeon(difficulty):
    """
    Genera un dungeon con miniboss e un boss principale.
    Se la lista di item è vuota, i drop saranno vuoti.
    I parametri variano in base alla difficoltà.
    Difficoltà possibili: "E", "D", "C", "F", "A", "S"
    """
    dungeons = load_dungeons()
    dungeon_id = str(uuid.uuid4())

    if difficulty == "E":
        num_miniboss = random.randint(1, 2)
        drop_count = 1
        money = random.randint(500, 1000)
        exp_reward = random.randint(100, 200)
    elif difficulty == "D":
        num_miniboss = random.randint(2, 3)
        drop_count = random.choices([1, 2], weights=[0.7, 0.3])[0]
        money = random.randint(1000, 1500)
        exp_reward = random.randint(200, 300)
    elif difficulty == "C":
        num_miniboss = random.randint(2, 3)
        drop_count = 2
        money = random.randint(1500, 2000)
        exp_reward = random.randint(500, 400)
    elif difficulty == "B":
        num_miniboss = random.randint(3, 4)
        drop_count = 2
        money = random.randint(2000, 3000)
        exp_reward = random.randint(1000, 1300)
    elif difficulty == "A":
        num_miniboss = random.randint(3, 4)
        drop_count = 3
        money = random.randint(3000, 4000)
        exp_reward = random.randint(1800, 2500)
    elif difficulty == "S":
        num_miniboss = random.randint(4, 6)
        drop_count = 3
        money = random.randint(4000, 6000)
        exp_reward = random.randint(4000, 5000)
    else:
        return None

    encounters = []
    for _ in range(num_miniboss):
        miniboss = get_predefined_boss()
        if miniboss:
            drops = get_random_drops(drop_count, user_grade=difficulty)
            encounters.append({
                "tipo": "miniboss",
                "nemico": miniboss,
                "drops": drops
            })

    main_boss = get_predefined_boss()
    if not main_boss:
        return None

    boss_drops = get_random_drops(drop_count, user_grade=difficulty)
    encounters.append({
        "tipo": "boss",
        "nemico": main_boss,
        "drops": boss_drops
    })

    dungeon = {
        "id": dungeon_id,
        "difficulty": difficulty,
        "encounters": encounters,
        "money": money,
        "exp_reward": exp_reward,
        "participants": []
    }
    dungeons[dungeon_id] = dungeon
    save_dungeons(dungeons)
    return dungeon


def complete_dungeon(dungeon_id, outcome, user_id):
    """
    Se outcome == "successo", oltre a soldi ed EXP, estraiamo i drop e li aggiungiamo all'inventario dell'utente.
    Restituiamo un messaggio con i dettagli dei drop ottenuti.
    """
    print("[DEBUG] Inizio complete_dungeon()")
    print("[DEBUG] dungeon_id:", dungeon_id, "outcome:", outcome, "user_id:", user_id)
    
    dungeons = load_dungeons()
    if dungeon_id not in dungeons:
        print("[DEBUG] Dungeon non trovato.")
        return "Dungeon non trovato."
    
    dungeon = dungeons[dungeon_id]
    print("[DEBUG] Dungeon trovato:", dungeon_id)
    
    if outcome.lower() != "successo":
        print("[DEBUG] Outcome non successo.")
        return "Dungeon completato con esito negativo, nessun premio assegnato."
    
    users = load_users()
    user_key = str(user_id)
    if user_key not in users:
        print("[DEBUG] Utente non registrato: user_id", user_id)
        return "Utente non registrato."
    
    user = users[user_key]
    print("[DEBUG] Utente trovato:", user)

    # Aggiorna premi base
    user["dungeons_completed"] = user.get("dungeons_completed", 0) + 1
    user["money"] = user.get("money", 0) + dungeon["money"]
    user["exp"] += dungeon["exp_reward"]
    print("[DEBUG] Premi base aggiornati: soldi =", user["money"], ", EXP =", user["exp"])

    drop_count = random.randint(1, 3)
    print("[DEBUG] Numero di drop estratti:", drop_count)
    drop_items = get_random_drops(drop_count, user_grade=user["rank"])
    
    print("[DEBUG] Drop items estratti:", drop_items)

    if "inventory" not in user:
        user["inventory"] = []
    
    print(drop_items)
    drops_message = ""
    for itm in drop_items:
        user["inventory"].append(itm)
        drops_message += (
            f"\n- <b>{itm['name']}</b>\n"
            f"   Grado: {itm['grade']}\n"
            f"   Tipo: {itm['type']}\n"
            f"   Descrizione: {itm['description']}\n"
            f"   Effetto: {itm['effect']}\n"
            f"   Abilità: {itm['ability']}\n"
        )

    save_users(users)
    print("[DEBUG] Dati utenti salvati.")
    print("[DEBUG] Inventario attuale:", user["inventory"])

    final_message = (
        f"Hai completato con successo il Dungeon {dungeon_id}!<br/>"
        f"Hai guadagnato {dungeon['money']} soldi e {dungeon['exp_reward']} EXP.<br/><br/>"
        f"<b>Drop ottenuti:</b>{drops_message}"
    )
    print("[DEBUG] Messaggio finale:", final_message)
    return final_message


from collections import defaultdict

def build_inventory_html(inventory_list):
    """
    Riceve una lista di item (dizionari) e produce un HTML con <details> e <summary>
    raggruppando per 'type'.
    """
    # Raggruppiamo per type
    inv_by_type = defaultdict(list)
    for item in inventory_list:
        item_type = item.get("type", "Sconosciuto")
        inv_by_type[item_type].append(item)

    html = ""
    # Per ogni tipologia, creiamo un blocco collapsible
    for ttype, items in inv_by_type.items():
        html += f"<details style='margin-bottom:8px;'>"
        html += f"<summary>{ttype} ({len(items)})</summary>"
        html += "<ul style='list-style:none; padding-left:1em;'>"
        for it in items:
            name = it.get("name", "Senza Nome")
            grade = it.get("grade", "?")
            desc = it.get("description", "")
            eff = it.get("effect", "")
            ability = it.get("ability", "")
            # Qui puoi personalizzare come vuoi visualizzare i dettagli
            html += f"<li style='margin-top:4px;'>"
            html += f"<b>{name}</b> (Grado: {grade})<br/>"
            html += f"<i>{desc}</i><br/>"
            html += f"Effetto: {eff}<br/>"
            html += f"Abilità: {ability}"
            html += "</li>"
        html += "</ul>"
        html += "</details>"
    return html


# Funzione per generare l'HTML del profilo utente
def get_user_profile_html(user_id):
    profile = get_user_profile(user_id)
    if not profile:
        return None
    inventory_html = build_inventory_html(profile.get("inventory", []))
    # Calcola i nuovi dati basati sull'EXP
    level = calculate_level(profile["exp"])
    exp_needed_level = exp_for_next_level(profile["exp"])
    calculated_rank = calculate_rank(profile["exp"])
    exp_needed_rank = exp_for_next_rank(profile["exp"])
    
    html_profile = (
        f"<h3>{profile['username']} (ID: {profile['user_id']})</h3>"
        f"<ul>"
        f"<li><strong>Grado calcolato:</strong> {calculated_rank}</li>"
        f"<li><strong>Level:</strong> {level}</li>"
        f"<li><strong>EXP:</strong> {profile['exp']} (Mancano {exp_needed_level} per il prossimo livello)</li>"
        f"<li><strong>EXP per salire di grado:</strong> {exp_needed_rank}</li>"
        f"<li><strong>Soldi:</strong> {profile['money']}</li>"
        f"<li><strong>Dungeon completati:</strong> {profile['dungeons_completed']}</li>"
        f"</ul>"
        f"<h4>Inventario</h4>"
        f"{inventory_html}"
    )
    return html_profile


def get_user_profile_json(user_id):
    user_data = get_user_profile(user_id)
    if not user_data:
        return None
    inventory_html = build_inventory_html(user_data["inventory"])
    user_data["inventory_html"] = inventory_html
    return user_data


def calculate_level(exp):
    """
    Calcola il livello dell'utente in base all'EXP totale.
    Usando una curva quadratica: per passare dal livello L al livello L+1
    sono necessari 100*(L^2) EXP totali.
    Livello 1: 0-99 EXP, Livello 2: 100-399 EXP, Livello 3: 400-899 EXP, ecc.
    Il livello massimo è 20.
    """
    level = 1
    while level < 20 and exp >= 100 * (level ** 2):
        level += 1
    return level

def exp_for_next_level(exp):
    """
    Restituisce la EXP necessaria per raggiungere il livello successivo.
    Se il livello corrente è 20, ritorna 0.
    """
    level = calculate_level(exp)
    if level >= 20:
        return 0
    next_threshold = 100 * (level ** 2)
    return next_threshold - exp

def calculate_rank(exp):
    """
    Determina il grado (rank) in base al livello.
    Ad esempio:
      - Livello 1-4: Grado "E"
      - Livello 5-7: Grado "D"
      - Livello 8-10: Grado "C"
      - Livello 11-13: Grado "B"
      - Livello 14-16: Grado "A"
      - Livello 17-20: Grado "S"
    """
    level = calculate_level(exp)
    if level < 5:
        return "E"
    elif level < 8:
        return "D"
    elif level < 11:
        return "C"
    elif level < 14:
        return "B"
    elif level < 17:
        return "A"
    else:
        return "S"

def exp_for_next_rank(exp):
    """
    Restituisce la EXP necessaria per raggiungere il grado successivo.
    Se l'utente ha grado "S", ritorna 0.
    Le soglie sono definite in base al livello:
      - Per passare da "E" a "D", serve arrivare al livello 5 (100*5^2 = 2500 EXP totali)
      - Da "D" a "C": livello 8 (100*8^2 = 6400 EXP)
      - Da "C" a "B": livello 11 (100*11^2 = 12100 EXP)
      - Da "B" a "A": livello 14 (100*14^2 = 19600 EXP)
      - Da "A" a "S": livello 17 (100*17^2 = 28900 EXP)
    """
    current_rank = calculate_rank(exp)
    if current_rank == "S":
        return 0
    rank_next_level = {
        "E": 5,
        "D": 8,
        "C": 15,
        "B": 15,
        "A": 17
    }
    next_threshold = 100 * (rank_next_level[current_rank] ** 2)
    return next_threshold - exp

def update_user_grade(user_id):
    """
    Calcola il nuovo grado basato sull'EXP e aggiorna il record dell'utente.
    Ritorna il nuovo grado.
    """
    users = load_users()
    if user_id in users:
        exp_total = users[user_id]["exp"]
        new_grade = calculate_rank(exp_total)
        users[user_id]["rank"] = new_grade
        save_users(users)
        return new_grade
    return None

