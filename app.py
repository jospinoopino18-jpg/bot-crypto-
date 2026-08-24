import requests, time, yfinance as yf
from ta.momentum import RSIIndicator
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta
import os

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

def get_rsi(symbol, interval, period):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if len(df) < 50: return None
        close = df['Close'].squeeze()
        rsi = RSIIndicator(close, window=14).rsi().iloc[-1]
        return float(rsi)
    except:
        return None

def check():
    now = datetime.now()
    for sym in PAIRES:
        rsi15 = get_rsi(sym, "15m", "2d")
        rsi1h = get_rsi(sym, "1h", "7d")
        if rsi15 is None or rsi1h is None: continue

        name = NAMES[sym]
        # ETAT ACTUEL
        etat = "CALME"
        if rsi15 > 60 and rsi1h > 60: etat = "ACHAT"
        elif rsi15 < 40 and rsi1h < 40: etat = "VENTE"

        ancien = dernier_etat.get(sym, "CALME")

        # 1. NOUVEAU SIGNAL TENDANCE
        if etat!= ancien and etat!= "CALME":
            # anti spam 5 min pour nouveau signal
            if sym not in dernier_envoi or (now - dernier_envoi[sym]) > timedelta(minutes=5):
                emoji = "🟢" if etat=="ACHAT" else "🔴"
                send(f"{emoji} *{name} {etat} V6.1*\nRSI 15m: {rsi15:.1f} >/< 60/40\nRSI 1H: {rsi1h:.1f}\nHeure: {now.strftime('%H:%M')}")
                dernier_envoi[sym] = now

        # 2. CORRECTION IMMEDIATE QUE TU VOULAIS
        if ancien == "ACHAT" and rsi15 < 60:
            send(f"⚠️ *{name} FIN ACHAT / STOP*\nRSI 15m repasse sous 60: {rsi15:.1f}\nRSI 1H: {rsi1h:.1f}\nPrenez TP / Sortez")

        if ancien == "VENTE" and rsi15 > 40:
            send(f"⚠️ *{name} FIN VENTE / STOP*\nRSI 15m repasse au dessus de 40: {rsi15:.1f}\nRSI 1H: {rsi1h:.1f}\nPrenez TP / Sortez")

        # 3. CALME toutes les 15 min
        if etat == "CALME":
            if sym not in dernier_calme or (now - dernier_calme[sym]) > timedelta(minutes=15):
                send(f"⚪ *{name} CALME*\nRSI 15m: {rsi15:.1f} | RSI 1H: {rsi1h:.1f} | Entre 40-60")
                dernier_calme[sym] = now

        dernier_etat[sym] = etat
        print(f"{now.strftime('%H:%M')} {name} {etat} | {rsi15:.1f} | {rsi1h:.1f}")

# Flask pour Render
app = Flask('')
@app.route('/')
def home(): return "Bot V6.1 STOP immediat en ligne"
Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

send("🚀 *Bot V6.1 lancé - STOP immédiat actif*")
while True:
    check()
    time.sleep(60)
