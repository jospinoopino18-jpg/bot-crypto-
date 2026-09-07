import requests, time, threading
from flask import Flask

TOKEN = "8606332059:AAFhaW3DocdsC-0byBHhkLfaTy-UhktOBTo"  # celui qui a marché pour le TEST
CHAT_ID = "7335134261"

app = Flask(__name__)

def loop():
    requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": "BOT ENFIN EN LIGNE 🚀"})
    while True:
        time.sleep(60)

threading.Thread(target=loop, daemon=True).start()

@app.route('/')
def home():
    return "BOT OK"

app.run(host='0.0.0.0', port=10000)
