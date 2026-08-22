import yfinance as yf
import pandas as pd
import ta
import time
import requests
import os
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot V4 - Filtre 15m+1h actif"

# --- COLLE TES INFOS ICI ---
BOT_TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
# ---------------------------

COINS = ["BTC-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD"]

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: 
        pass

def get_rsi(symbol, period, interval):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if len(df) < 20: return 50
        close = df['Close']
        if isinstance(close, pd.DataFrame): close = close.squeeze()
        rsi = float(ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1])
        return rsi
    except: 
        return 50

def bot_loop():
    time.sleep(5)
    send_telegram("✅ Bot V4 lancé - J'envoie que si 15m ET 1h sont d'accord")
    while True:
        signal_trouve_ce_tour = False
        
        for coin in COINS:
            rsi_15 = get_rsi(coin, "2d", "15m")
            rsi_1h = get_rsi(coin, "5d", "1h")
            
            # FILTRE QU'ON A PREVU
            if rsi_15 > 52 and rsi_1h > 52:
                send_telegram(f"🚀 STRONG BUY {coin}\n15m: {rsi_15:.1f} | 1h: {rsi_1h:.1f}")
                signal_trouve_ce_tour = True
            elif rsi_15 < 48 and rsi_1h < 48:
                send_telegram(f"🔻 STRONG SELL {coin}\n15m: {rsi_15:.1f} | 1h: {rsi_1h:.1f}")
                signal_trouve_ce_tour = True
            else:
                print(f"{coin} pas aligné 15m:{rsi_15:.1f} 1h:{rsi_1h:.1f} -> j'ignore")
        
        # --- NOUVEAUTE : si aucun signal pendant ce cycle de 15min ---
        if not signal_trouve_ce_tour:
            send_telegram("⏳ Pas de signaux depuis 15 minutes. Aucun coin n'est aligné en 15m + 1h.")
        
        time.sleep(900) # 15 minutes

Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
