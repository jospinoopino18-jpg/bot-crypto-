import requests, time, yfinance as yf, pandas as pd
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

BOT_TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
PAIRES = ['BTC-USD','ETH-USD','SOL-USD','DOGE-USD','SHIB-USD','AVAX-USD']
NAMES = {'BTC-USD':'BTC','ETH-USD':'ETH','SOL-USD':'SOL','DOGE-USD':'DOGE','SHIB-USD':'SHIB','AVAX-USD':'AVAX'}

dernier_etat = {}
dernier_envoi = {}
dernier_calme = {}

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: pass

def rsi_calculate(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).ewm(alpha=1/period, adjust=False).mean()
    loss = -delta.where(delta < 0, 0).ewm(alpha=1/period, adjust=False).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi.iloc[-1]

def get_rsi(symbol, interval, period):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if len(df) < 50: return None
        return float(rsi_calculate(df['Close']))
    except:
        return None

def check():
    now = datetime.now()
    for sym in PAIRES:
        rsi15 = get_rsi(sym, "15m", "2d")
        rsi1h = get_rsi(sym, "1h", "7d")
        if rsi15 is None or rsi1h is None: continue

        name = NAMES[sym]
        etat = "CALME"
        if rsi15 > 60 and rsi1h > 60: etat = "ACHAT"
        elif rsi15 < 40 and rsi1h < 40: etat = "VENTE"
        ancien = dernier_etat.get(sym, "CALME")

        if etat!= ancien and etat!= "CALME":
            if sym not in dernier_envoi or (now - dernier_envoi[sym]) > timedelta(minutes=5):
                emoji = "🟢" if etat=="ACHAT" else "🔴"
                send(f"{emoji} *{name} {etat} V6.1*\nRSI 15m: {rsi15:.1f}\nRSI 1H: {rsi1h:.1f}\n{now.strftime('%H:%M')}")
                dernier_envoi[sym] = now

        # STOP IMMEDIAT
        if ancien == "ACHAT" and rsi15 < 60:
            send(f"⚠️ *{name} FIN ACHAT / STOP*\nRSI 15m repasse sous 60: {rsi15:.1f}")
        if ancien == "VENTE" and rsi15 > 40:
            send(f"⚠️ *{name} FIN VENTE / STOP*\nRSI 15m repasse au dessus 40: {rsi15:.1f}")

        if etat == "CALME":
            if sym not in dernier_calme or (now - dernier_calme[sym]) > timedelta(minutes=15):
                send(f"⚪ *{name} CALME* | 15m:{rsi15:.1f} 1H:{rsi1h:.1f}")
                dernier_calme[sym] = now

        dernier_etat[sym] = etat
        print(f"{name} {etat} {rsi15:.1f}/{rsi1h:.1f}")

app = Flask('')
@app.route('/')
def home(): return "Bot V6.1 en ligne"
Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

send("🚀 *Bot V6.1 FIX lancé - STOP immédiat actif*")
while True:
    check()
    time.sleep(60)
