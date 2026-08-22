from flask import Flask
import requests, threading, time
from datetime import datetime

app = Flask(__name__)

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
COINS = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "DOGE-USD"]

dernier_signal_envoye = {}
last_no_signal = 0

def send_telegram(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def get_rsi(symbol, interval):
    try:
        url = f"https://api.twelvedata.com/rsi?symbol={symbol}&interval={interval}&apikey=demo"
        r = requests.get(url, timeout=10).json()
        return float(r['values'][0]['rsi']) if 'values' in r else None
    except: return None

def bot_loop():
    global last_no_signal
    send_telegram("✅ Bot V4.2 ULTRA REACTIF (1 min + anti-spam 45min) lancé")
    while True:
        signal_trouve = False
        for coin in COINS:
            rsi_15m = get_rsi(coin, "15min")
            rsi_1h = get_rsi(coin, "1h")
            if rsi_15m is None or rsi_1h is None: continue
            type_signal = None
            if rsi_15m > 52 and rsi_1h > 52: type_signal = "BUY"
            elif rsi_15m < 48 and rsi_1h < 48: type_signal = "SELL"
            if type_signal:
                cle = f"{coin}_{type_signal}"
                if cle in dernier_signal_envoye and time.time() - dernier_signal_envoye[cle] < 2700:
                    signal_trouve = True
                    continue
                signal_trouve = True
                dernier_signal_envoye[cle] = time.time()
                if type_signal == "BUY":
                    send_telegram(f"🚀 STRONG BUY {coin}\n15m: {rsi_15m:.1f} | 1h: {rsi_1h:.1f}\n{datetime.now().strftime('%H:%M')}")
                else:
                    send_telegram(f"🔻 STRONG SELL {coin}\n15m: {rsi_15m:.1f} | 1h: {rsi_1h:.1f}\n{datetime.now().strftime('%H:%M')}")
        if not signal_trouve:
            if time.time() - last_no_signal > 900:
                send_telegram(f"⏳ Calme plat - aucun aligné 15m+1h {datetime.now().strftime('%H:%M')}")
                last_no_signal = time.time()
        time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home(): return "Bot V4.2 Live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
