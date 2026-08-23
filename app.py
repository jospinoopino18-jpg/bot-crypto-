from flask import Flask
import requests, threading, time, yfinance as yf
import pandas_ta as ta
from datetime import datetime

app = Flask(__name__)
TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
COINS = ["BTC-USD", "ETH-USD"]

def send_telegram(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def get_rsi_debug(symbol, interval):
    try:
        period = "5d" if interval == "15m" else "1mo"
        tf = "15m" if interval == "15m" else "1h"
        df = yf.download(symbol, period=period, interval=tf, progress=False, auto_adjust=True)
        if len(df) < 20:
            send_telegram(f"⚠️ DEBUG {symbol} {interval}: seulement {len(df)} bougies")
            return None
        df['RSI'] = ta.rsi(df['Close'], length=14)
        rsi = float(df['RSI'].iloc[-1])
        return rsi
    except Exception as e:
        send_telegram(f"❌ ERREUR {symbol} {interval}: {str(e)[:200]}")
        return None

def bot_loop():
    send_telegram("✅ Bot DEBUG V4.3 lancé - je vais dire pourquoi ça bloque")
    time.sleep(10)
    for coin in COINS:
        rsi_15 = get_rsi_debug(coin, "15m")
        rsi_1h = get_rsi_debug(coin, "1h")
        send_telegram(f"🔍 TEST {coin}\n15m: {rsi_15}\n1h: {rsi_1h}")
    # ensuite boucle normale...

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home(): return "Debug Live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
