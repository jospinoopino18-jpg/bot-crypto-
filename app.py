import os, time, requests, yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from flask import Flask
import threading

# --- CONFIG TELEGRAM ---
TOKEN = "8606332059:AAFhaW3DocdsC-0byBHhkLfaTy-UhktOBTo"
CHAT_ID = "7335134261"
PAIRES = {"EURUSD=X": "EURUSD", "GBPUSD=X": "GBPUSD"}

# --- MEMOIRE IA QUI APPREND ---
memoire = {
    "EURUSD": {"etat": "CALME", "seuil": 60.5, "loss": 0, "last_stop": None},
    "GBPUSD": {"etat": "CALME", "seuil": 60.5, "loss": 0, "last_stop": None},
}

def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=10)
        print(msg)
    except Exception as e: print(e)

def rsi_wilder(closes, period=14):
    deltas = [closes[i]-closes[i-1] for i in range(1,len(closes))]
    gains = [max(d,0) for d in deltas]
    losses = [max(-d,0) for d in deltas]
    avg_gain = sum(gains[:period])/period
    avg_loss = sum(losses[:period])/period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain*(period-1)+gains[i])/period
        avg_loss = (avg_loss*(period-1)+losses[i])/period
    if avg_loss==0: return 100.0
    return 100 - (100/(1+avg_gain/avg_loss))

def get_rsi(symbol, interval):
    try:
        # interval: 60m pour H1, 240m pour H4 n'existe pas chez yahoo -> on prend 1h et 4h via resample
        data = yf.download(symbol, period="10d", interval="1h", progress=False)
        if len(data)<100: return 50, 50
        closes = data['Close'].tolist()
        rsi1h = rsi_wilder(closes[-100:])

        # Créer H4 en resamplant H1
        df_4h = data.resample('4H').agg({'Close':'last'}).dropna()
        closes_4h = df_4h['Close'].tolist()
        rsi4h = rsi_wilder(closes_4h[-100:]) if len(closes_4h)>20 else 50

        return round(rsi1h,2), round(rsi4h,2)
    except: return 50, 50

def session_londres():
    # GMT time
    now_gmt = datetime.utcnow()
    # Londres 07h-12h GMT = meilleur moment forex
    if 7 <= now_gmt.hour < 12: return True
    return False

def news_block():
    # Bloque 13h30-16h00 GMT = news US (CPI, NFP, FOMC) qui font ton 60.4->59.8
    now_gmt = datetime.utcnow()
    if 13 <= now_gmt.hour < 16: return True
    return False

def check():
    if not session_londres():
        print("Hors session Londres - IA dort")
        return
    if news_block():
        print("Bloc news US - IA dort")
        return

    now = datetime.now()
    for sym, name in PAIRES.items():
        rsi1h, rsi4h = get_rsi(sym, "1h")
        mem = memoire[name]

        # ANTI-WHIPSAW 60min comme on a corrigé ton screen 17:26/17:27
        if mem["last_stop"] and (now - mem["last_stop"]) < timedelta(minutes=60):
            print(f"{name} bloqué 60min")
            continue

        # ADAPTATION: si 2 pertes, seuil 60.5 -> 62
        seuil = 62.0 if mem["loss"]>=2 else mem["seuil"]

        etat = "CALME"
        if rsi4h > 60 and rsi1h > seuil: etat = "ACHAT" # H4 boussole + H1 entrée
        if rsi4h < 40 and rsi1h < 40: etat = "VENTE"

        # Entrée
        if etat!= "CALME" and etat!= mem["etat"]:
            # Contexte comme tu voulais "comme toi"
            try:
                fear = requests.get("https://api.alternative.me/fng/?limit=1", timeout=5).json()['data'][0]['value']
                contexte = f"F&G:{fear}"
            except: contexte=""

            send(f"🟢 *{name} {etat} FOREX* | 1H:{rsi1h} 4H:{rsi4h} Seuil:{seuil} {contexte}\nSession Londres | Vol normale")
            mem["etat"]=etat
            mem["loss"]= max(0, mem["loss"]-1) # récompense si on retrouve un trade

        # Sortie avec hystérésis 59.5
        if mem["etat"]=="ACHAT" and rsi1h < 59.5:
            send(f"⚠️ *{name} FIN ACHAT / STOP* | 1H:{rsi1h}")
            mem["etat"]="CALME"; mem["last_stop"]=now; mem["loss"]+=1
            # IA apprend : si perte, monte seuil pour cette paire
            if mem["loss"]>=2: mem["seuil"]=62.0

        if mem["etat"]=="VENTE" and rsi1h > 40.5:
            send(f"⚠️ *{name} FIN VENTE / STOP* | 1H:{rsi1h}")
            mem["etat"]="CALME"; mem["last_stop"]=now; mem["loss"]+=1

# --- FLASK KEEPALIVE ---
app = Flask(__name__)
@app.route('/')
def home(): return "Mini-Moi FOREX V2 en vie"
threading.Thread(target=lambda: app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000))), daemon=True).start()

send("🧠 *Mini-Moi FOREX V2 lancée*\nPaires: EURUSD, GBPUSD\nSession: 07h-12h GMT uniquement\nAnti-whipsaw 60min + Seuil adaptatif")
while True:
    check()
    time.sleep(60)
