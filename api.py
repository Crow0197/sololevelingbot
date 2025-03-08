from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from funzioni_solo_leveling import (
    register_user,
    load_users,
    fight_boss,
    rank_up_user,
    simulate_boss_battle_messages,
    generate_dungeon,
    complete_dungeon,
    EXP_THRESHOLDS,
    update_user_grade,
    calculate_level,
    exp_for_next_level,
    calculate_rank,
    exp_for_next_rank

)
import re

app = FastAPI(title="Solo Leveling Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In produzione, specifica gli URL consentiti
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserRegister(BaseModel):
    user_id: str
    username: str

class UserCommand(BaseModel):
    user_id: int

class DungeonRequest(BaseModel):
    difficulty: str  # "B", "A" o "S"

class DungeonComplete(BaseModel):
    dungeon_id: str
    outcome: str
    user_id: int

@app.get("/profile/{username}", summary="Visualizza il profilo dell'utente per username")
def api_get_profile(username: str):
    users = load_users()
    for uid, user in users.items():
        if user.get("username", "").lower() == username.lower():
            # Aggiorniamo il grado in base all'EXP e salviamo il record
            update_user_grade(uid)
            # Ricarichiamo l'utente aggiornato
            user = load_users()[uid]
            exp_total = user["exp"]
            level = calculate_level(exp_total)
            exp_needed_level = exp_for_next_level(exp_total)
            calculated_rank = calculate_rank(exp_total)
            exp_needed_rank = exp_for_next_rank(exp_total)
            return {
                "username": user["username"],
                "user_id": uid,
                "rank": user["rank"],                # Grado salvato (aggiornato)
                "calculated_rank": calculated_rank,   # Grado calcolato in base all'EXP
                "level": level,
                "exp": exp_total,
                "exp_threshold": EXP_THRESHOLDS.get(user["rank"], "N/A"),
                "exp_needed_level": exp_needed_level,
                "exp_needed_rank": exp_needed_rank,
                "money": user.get("money", 0),
                "inventory": user.get("inventory", []),
                "dungeons_completed": user.get("dungeons_completed", 0)
            }
    raise HTTPException(status_code=404, detail="Utente non trovato")


@app.post("/register", summary="Registra un utente")
def api_register_user(user: UserRegister):
    result = register_user(user.user_id, user.username)
    return {"message": result}

@app.post("/fight", summary="Simula un combattimento contro un boss")
def api_fight_boss(command: UserCommand):
    result = fight_boss(command.user_id)
    return {"message": result}

@app.post("/rankup", summary="Controlla e applica l'avanzamento di grado")
def api_rankup(command: UserCommand):
    result = rank_up_user(command.user_id)
    return {"message": result}

@app.get("/bossbattle", summary="Simula la battaglia contro un boss")
def api_boss_battle():
    messages, avatar_url = simulate_boss_battle_messages()
    if messages is None:
        raise HTTPException(status_code=404, detail="Nessun boss disponibile")
    
    html_content = '<div style="max-height:400px; overflow-y:auto;">'
    for line in messages:
        safe_line = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", line)
        safe_line = re.sub(r"\*(.*?)\*", r"<i>\1</i>", safe_line)
        html_content += f"<p>{safe_line}</p>"
    html_content += "</div>"

    return {
        "messages": messages,
        "avatar_url": avatar_url,
        "bossbattle_html": html_content
    }

@app.post("/dungeon", summary="Genera un dungeon completo")
def api_generate_dungeon(req: DungeonRequest):
    dungeon = generate_dungeon(req.difficulty)
    if dungeon is None:
        raise HTTPException(status_code=400, detail="Difficoltà non valida o errore nella generazione del dungeon.")
    return {"dungeon": dungeon}

@app.post("/dungeon/summary", summary="Genera un dungeon e restituisce un riepilogo degli incontri")
def api_generate_dungeon_summary(req: DungeonRequest):
    dungeon = generate_dungeon(req.difficulty)
    if dungeon is None:
        raise HTTPException(status_code=400, detail="Difficoltà non valida o errore nella generazione del dungeon.")
    encounters_summary = []
    for encounter in dungeon["encounters"]:
        if "nemico" in encounter and "nome" in encounter["nemico"]:
            encounters_summary.append({
                "tipo": encounter["tipo"],
                "nome": encounter["nemico"]["nome"]
            })
    summary = {
        "id": dungeon["id"],
        "difficulty": dungeon["difficulty"],
        "encounters": encounters_summary,
        "money": dungeon["money"],
        "exp_reward": dungeon["exp_reward"]
    }
    return {"dungeon": summary}

@app.post("/dungeon/complete", summary="Completa un dungeon e assegna i premi")
def api_complete_dungeon(data: DungeonComplete):
    result = complete_dungeon(data.dungeon_id, data.outcome, data.user_id)
    print(result)
    if result.startswith("Dungeon non trovato") or result.startswith("Utente non registrato"):
        raise HTTPException(status_code=404, detail=result)
    return {"message": result}


@app.get("/profile_html/{username}")
def api_get_profile_html(username: str):
    users = load_users()
    user_id = None
    for uid, user in users.items():
        if user.get("username", "").lower() == username.lower():
            user_id = uid
            break
    if not user_id:
        raise HTTPException(status_code=404, detail="Utente non trovato")
    profile_html = get_user_profile_html(user_id)
    return {"profile_html": profile_html}
