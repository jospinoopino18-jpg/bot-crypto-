import requests, time, yfinance as yf, matplotlib.pyplot as plt, io
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

BOT_TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
PAIRES = ['BTC-USD','ETH-USD','SOL-USD','DOGE-USD','SHIB-USD','AVAX-USD']
NAMES = {'BTC-USD':'BTC','ETH-USD':'ETH','SOL-USD':'SOL','DOGE-USD':'DOGE','SHIB-USD':'SHIB','AVAX-USD':'AVAX'}

dernier_etat, dernier_calme, a_deja_stop = {}, {}, {}

def send(msg):
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)

def send_chart(sym, rsi15_val, rsi1h_val):
    try:
        df = yf.download(sym, period="1d", interval="15m", progress=False, auto_adjust=True)
        if df.empty: return
        close = df['Close'].squeeze()
        delta = close.diff()
        gain = delta.where(delta>0,0).ewm(alpha=1/14, adjust=False).mean()
        loss = -delta.where(delta<0,0).ewm(alpha=1/14, adjust=False).mean()
        rsi = 100 - (100/(1+gain/loss))

        plt.figure(figsize=(6,3))
        plt.plot(rsi.tail(50).values, label='RSI 15m')
        plt.axhline(60, color='green', linestyle='--'); plt.axhline(40, color='red', linestyle='--')
        plt.title(f"{NAMES[sym]} RSI 15m - Actuel {rsi15_val:.1f} | H1 {rsi1h_val:.1f}")
        plt.ylim(20,80); plt.legend()
        buf = io.BytesIO(); plt.savefig(buf, format='png', dpi=120, bbox_inches='tight'); plt.close()
        buf.seek(0)
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={"chat_id": CHAT_ID}, files={"photo": buf}, timeout=15)
    except Exception as e:
        print(e)

def get_rsi(symbol, interval, period):
    try:
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True, threads=False)
        if df.empty or len(df)<30: return None
        close = df['Close'].squeeze()
        delta = close.diff()
        gain = delta.where(delta>0,0).ewm(alpha=1/14, adjust=False).mean()
        loss = -delta.where(delta<0,0).ewm(alpha=1/14, adjust=False).mean()
        return float((100 - (100/(1+gain/loss))).iloc[-1])
    except: return None

def check():
    now = datetime.now()
    for sym in PAIRES:
        rsi15 = get_rsi(sym, "15m", "2d"); time.sleep(1)
        rsi1h = get_rsi(sym, "1h", "7d"); time.sleep(1)
        if rsi15 is None or rsi1h is None: continue
        name=NAMES[sym]; etat="CALME"
        if rsi15>60 and rsi1h>60: etat="ACHAT"
        elif rsi15<40 and rsi1h<40: etat="VENTE"
        ancien = dernier_etat.get(sym,"PREMIER")

        if etat in ["ACHAT","VENTE"] and ancien!=etat:
            send(f"{'🟢' if etat=='ACHAT' else '🔴'} {name} {etat} POSSIBLE | 15m:{rsi15:.1f} 1H:{rsi1h:.1f} -> Confirme visuellement")
            send_chart(sym, rsi15, rsi1h)
            a_deja_stop[sym]=False; dernier_calme.pop(sym,None)

        if ancien=="ACHAT" and rsi15<60 and not a_deja_stop.get(sym,False):
            send(f"⚠️ {name} FIN ACHAT / STOP | 15m:{rsi15:.1f}"); a_deja_stop[sym]=True
        if ancien=="VENTE" and rsi15>40 and not a_deja_stop.get(sym,False):
            send(f"⚠️ {name} FIN VENTE / STOP | 15m:{rsi15:.1f}"); a_deja_stop[sym]=True

        if etat=="CALME":
            if sym not in dernier_calme or (now - dernier_calme[sym]) >= timedelta(minutes=15):
                send(f"⚪ {name} CALME | 15m:{rsi15:.1f} 1H:{rsi1h:.1f}"); dernier_calme[sym]=now
        if ancien!=etat or ancien=="PREMIER": dernier_etat[sym]=etat

app = Flask('')
@app.route('/')
def home(): return "V7 VISUEL"
Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()
send("👁️ V7 VISUELLE lancée | Photo RSI à chaque signal | CALME 15min")
while True:
    t0=time.time(); check(); time.sleep(max(10, 60-(time.time()-t0)))
