import requests, time, yfinance as yf
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

BOT_TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
PAIRES = ['BTC-USD','ETH-USD','SOL-USD','DOGE-USD','SHIB-USD','AVAX-USD']
NAMES = {'BTC-USD':'BTC','ETH-USD':'ETH','SOL-USD':'SOL','DOGE-USD':'DOGE','SHIB-USD':'SHIB','AVAX-USD':'AVAX'}

dernier_etat = {}
dernier_calme = {}
a_deja_stop = {}

def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
    except: pass

def get_rsi(symbol, interval, period):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True, threads=False)
        if df.empty or len(df)<30: return None
        close = df['Close']
        if hasattr(close, 'columns'): close = close.squeeze()
        delta = close.diff()
        gain = delta.where(delta>0,0).ewm(alpha=1/14, adjust=False).mean()
        loss = -delta.where(delta<0,0).ewm(alpha=1/14, adjust=False).mean()
        return float((100 - (100/(1+gain/loss))).iloc[-1])
    except: return None

def check():
    now = datetime.now()
    for sym in PAIRES:
        rsi15 = get_rsi(sym, "15m", "2d")
        time.sleep(2)
        rsi1h = get_rsi(sym, "1h", "7d")
        time.sleep(2)
        if rsi15 is None or rsi1h is None: continue

        name = NAMES[sym]
        etat = "CALME"
        if rsi15>60 and rsi1h>60: etat="ACHAT"
        elif rsi15<40 and rsi1h<40: etat="VENTE"
        ancien = dernier_etat.get(sym, "PREMIER")

        # 1. NOUVEL ACHAT/VENTE une seule fois
        if etat in ["ACHAT","VENTE"] and ancien!= etat:
            send(f"{'🟢' if etat=='ACHAT' else '🔴'} {name} {etat} | 15m:{rsi15:.1f} 1H:{rsi1h:.1f}")
            a_deja_stop[sym]=False
            dernier_calme.pop(sym, None)

        # 2. STOP une seule fois (corrige ton spam 14:33 / 14:39)
        if ancien=="ACHAT" and rsi15<60 and not a_deja_stop.get(sym, False):
            send(f"⚠️ {name} FIN ACHAT / STOP | 15m:{rsi15:.1f}")
            a_deja_stop[sym]=True
        if ancien=="VENTE" and rsi15>40 and not a_deja_stop.get(sym, False):
            send(f"⚠️ {name} FIN VENTE / STOP | 15m:{rsi15:.1f}")
            a_deja_stop[sym]=True

        # 3. CALME toutes les 15 MIN STRICT (corrige ton screen)
        if etat=="CALME":
            if sym not in dernier_calme or (now - dernier_calme[sym]) >= timedelta(minutes=15):
                send(f"⚪ {name} CALME | 15m:{rsi15:.1f} 1H:{rsi1h:.1f}")
                dernier_calme[sym]=now

        if ancien!= etat or ancien=="PREMIER":
            dernier_etat[sym]=etat
        print(f"{now.strftime('%H:%M:%S')} {name} {etat} {rsi15:.1f}/{rsi1h:.1f}")

app = Flask('')
@app.route('/')
def home(): return "V6.4 HORAIRE STRICT"
Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

send("🚀 V6.4 HORAIRE STRICT - V6 intacte | Check 1min | CALME 15min")
while True:
    t0=time.time()
    check()
    time.sleep(max(10, 60 - (time.time()-t0)))
