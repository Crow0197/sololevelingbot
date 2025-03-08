import threading
import uvicorn
from bot_solo_leveling import run_bot
from api import app

def start_bot():
    run_bot()

if __name__ == "__main__":
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.start()
    uvicorn.run(app, host="0.0.0.0", port=8000)
