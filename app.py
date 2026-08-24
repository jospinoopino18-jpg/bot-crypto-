import requests, time, yfinance as yf
from flask import Flask
from threading import Thread
from datetime import datetime, timedelta

BOT_TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
PAIRES = ['BTC-USD','ETH-USD','SOL-USD','DOGE-USD','SHIB-USD','AVAX-USD']
NAMES = {'BTC-USD':'BTC','ETH-USD':'ETH','SOL-USD':'SOL','DOGE-USD':'DOGE','SHIB-USD':'SHIB','AVAX-USD':'AVAX'}

dernier_etat = {}
def send(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except Exception as e:
        print(f"Erreur send {e}")

def get_rsi(symbol, interval, period):
    for _ in range(2):
        try:
            df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True, threads=False)
            if df.empty or len(df) < 30:
                time.sleep(2)
                continue
            close = df['Close']
            if hasattr(close, 'columns'): close = close.squeeze()
            delta = close.diff()
            gain = delta.where(delta > 0, 0).ewm(alpha=1/14, adjust=False).mean()
            loss = -delta.where(delta < 0, 0).ewm(alpha=1/14, adjust=False).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return float(rsi.iloc[-1])
        except Exception as e:
            print(f"Erreur RSI {symbol} {e}")
            time.sleep(2)
    return None

def check():
    print(f"--- SCAN {datetime.now().strftime('%H:%M:%S')} ---")
    for sym in PAIRES:
        rsi15 = get_rsi(sym, "15m", "2d")
        time.sleep(3) # anti-ban yahoo
        rsi1h = get_rsi(sym, "1h", "7d")
        time.sleep(3)
        if rsi15 is None or rsi1h is None:
            print(f"{sym} RSI None, skip")
            continue
        name = NAMES[sym]
        etat = "CALME"
        if rsi15 > 60 and rsi1h > 60: etat = "ACHAT"
        elif rsi15 < 40 and rsi1h < 40: etat = "VENTE"
        ancien = dernier_etat.get(sym, "PREMIER")

        if ancien == "PREMIER": # FORCAGE PREMIER SCAN
            if etat == "CALME":
                send(f"⚪ {name} CALME | 15m:{rsi15:.1f} 1H:{rsi1h:.1f}")
            else:
                send(f"{'🟢' if etat=='ACHAT' else '🔴'} {name} {etat} | 15m:{rsi15:.1f} 1H:{rsi1h:.1f}")
        else:
            if etat!=ancien and etat!="CALME":
                send(f"{'🟢' if etat=='ACHAT' else '🔴'} {name} {etat} | 15m:{rsi15:.1f} 1H:{rsi1h:.1f}")
            if ancien=="ACHAT" and rsi15<60:
                send(f"⚠️ {name} FIN ACHAT/STOP | 15m {rsi15:.1f}")
            if ancien=="VENTE" and rsi15>40:
                send(f"⚠️ {name} FIN VENTE/STOP | 15m {rsi15:.1f}")

        dernier_etat[sym] = etat
        print(f"{name} {etat} {rsi15:.1f}/{rsi1h:.1f}")

app = Flask('')
@app.route('/')
def home(): return "V6.2 en ligne"
Thread(target=lambda: app.run(host='0.0.0.0', port=10000)).start()

send("🚀 V6.2 SCAN FORCE lance - 1er scan dans 20sec")
while True:
    check()
    time.sleep(60)
