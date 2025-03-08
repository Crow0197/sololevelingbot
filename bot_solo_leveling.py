import telebot
from funzioni_solo_leveling import (
    register_user,
    get_user_profile,
    fight_boss,
    rank_up_user,
    simulate_boss_battle_messages,
    generate_dungeon,
    complete_dungeon
)

API_TOKEN = "1747322296:AAErysndaRCCuCOLBELeTUOGivhrgGYqIrk"  # Sostituisci con il tuo token Telegram
bot = telebot.TeleBot(API_TOKEN)

def run_bot():
    print("[DEBUG] Bot avviato. In attesa di comandi...")

    @bot.message_handler(commands=["register"])
    def register_command(message):
        print(f"[DEBUG] /register da {message.from_user.id} - {message.from_user.first_name}")
        user_id = str(message.from_user.id)
        username = message.from_user.first_name
        response = register_user(user_id, username)
        bot.reply_to(message, response)

    @bot.message_handler(commands=["profile"])
    def profile_command(message):
        print(f"[DEBUG] /profile da {message.from_user.id} - {message.from_user.first_name}")
        user_id = str(message.from_user.id)
        response = get_user_profile(user_id)
        bot.reply_to(message, response, parse_mode="Markdown")

    @bot.message_handler(commands=["fight"])
    def fight_command(message):
        print(f"[DEBUG] /fight da {message.from_user.id} - {message.from_user.first_name}")
        user_id = str(message.from_user.id)
        response = fight_boss(user_id)
        bot.reply_to(message, response, parse_mode="Markdown")

    @bot.message_handler(commands=["rankup"])
    def rankup_command(message):
        print(f"[DEBUG] /rankup da {message.from_user.id} - {message.from_user.first_name}")
        user_id = str(message.from_user.id)
        response = rank_up_user(user_id)
        bot.reply_to(message, response, parse_mode="Markdown")

    @bot.message_handler(commands=["bossbattle"])
    def boss_battle_command(message):
        print(f"[DEBUG] /bossbattle da {message.from_user.id} - {message.from_user.first_name}")
        messages, avatar_url = simulate_boss_battle_messages()
        if messages is None:
            bot.reply_to(message, "Nessun boss disponibile al momento.")
            return
        bot.send_photo(message.chat.id, avatar_url)
        for msg in messages:
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")

    @bot.message_handler(commands=["dungeon"])
    def dungeon_command(message):
        print(f"[DEBUG] /dungeon da {message.from_user.id} - {message.from_user.first_name}")
        try:
            parts = message.text.split()
            if len(parts) < 2:
                bot.reply_to(message, "Uso: /dungeon <difficoltà> (B, A o S)")
                return
            difficulty = parts[1].upper()
            dungeon = generate_dungeon(difficulty)
            if dungeon is None:
                bot.reply_to(message, "Difficoltà non valida o errore nella generazione del dungeon.")
                return
            response = (
                f"**Dungeon generato!**\n"
                f"ID: `{dungeon['id']}`\n"
                f"Difficoltà: {dungeon['difficulty']}\n"
                f"Numero di incontri: {len(dungeon['encounters'])}\n"
                f"Premio: {dungeon['money']} soldi, {dungeon['exp_reward']} EXP\n"
                f"Il dungeon è registrato. Completa il dungeon con: /dungeoncomplete <ID> <outcome>\n"
                f"(Outcome: successo o fallimento)"
            )
            bot.reply_to(message, response, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"Errore: {str(e)}")

    @bot.message_handler(commands=["dungeoncomplete"])
    def dungeon_complete_command(message):
        print(f"[DEBUG] /dungeoncomplete da {message.from_user.id} - {message.from_user.first_name}")
        try:
            parts = message.text.split()
            if len(parts) < 3:
                bot.reply_to(message, "Uso: /dungeoncomplete <dungeon_id> <outcome> (outcome: successo o fallimento)")
                return
            dungeon_id = parts[1]
            outcome = parts[2].lower()
            user_id = str(message.from_user.id)
            result = complete_dungeon(dungeon_id, outcome, user_id)
            bot.reply_to(message, result, parse_mode="Markdown")
        except Exception as e:
            bot.reply_to(message, f"Errore: {str(e)}")

    @bot.message_handler(func=lambda message: True)
    def fallback(message):
        print(f"[DEBUG] Messaggio non riconosciuto da {message.from_user.id}")
        bot.reply_to(message, "Comando non riconosciuto. Usa /help per la lista dei comandi.")

    bot.polling()

if __name__ == "__main__":
    run_bot()
