from flask import Flask
import requests, threading, time, yfinance as yf
from datetime import datetime

app = Flask(__name__)
TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"  # Mets ton nouveau token
CHAT_ID = "7335134261"

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def bot():
    send("✅ BOT V4.5 ULTRA SIMPLE DEPLOYÉ - enfin !")
    while True:
        try:
            btc = yf.download("BTC-USD", period="1d", interval="1h", progress=False)['Close'].iloc[-1]
            send(f"BTC: {btc:.2f}$ - Bot marche ! {datetime.now()}")
        except Exception as e:
            send(f"Erreur: {e}")
        time.sleep(900)

threading.Thread(target=bot, daemon=True).start()

@app.route("/")
def home(): return "OK V4.5"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
