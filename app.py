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
    return "Bot V4 Strong Trend Live - OK"

BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")
COINS = ["BTC-USD", "SOL-USD", "BNB-USD", "XRP-USD", "ADA-USD", "DOGE-USD"]

def send_telegram(msg):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": msg})
    except: pass

def get_rsi(symbol, period, interval):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        close = df['Close']
        if isinstance(close, pd.DataFrame): close = close.squeeze()
        rsi = ta.momentum.RSIIndicator(close, window=14).rsi().iloc[-1]
        return float(rsi)
    except:
        return 50

def bot_loop():
    while True:
        for coin in COINS:
            rsi_15 = get_rsi(coin, "2d", "15m")
            rsi_1h = get_rsi(coin, "5d", "1h")
            
            # SEULEMENT MEME TENDANCE
            if rsi_15 > 52 and rsi_1h > 52:
                send_telegram(f"🚀 STRONG BUY {coin} 15m:{rsi_15:.1f} 1h:{rsi_1h:.1f}")
            elif rsi_15 < 48 and rsi_1h < 48:
                send_telegram(f"🔻 STRONG SELL {coin} 15m:{rsi_15:.1f} 1h:{rsi_1h:.1f}")
        
        time.sleep(900) # 15 minutes

Thread(target=bot_loop, daemon=True).start()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
