from flask import Flask
import requests, threading, time, yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

app = Flask(__name__)
TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
COINS = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "DOGE-USD", "SHIB-USD"]

# MEMOIRE DES SIGNAUX
last_state = {} # coin -> "ACHAT" / "VENTE" / "CALME"
last_sent_time = {} # coin -> datetime

def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except: pass

def rsi_wilder(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    avg_gain = gain.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def get_rsi(symbol, interval):
    try:
        period = "5d" if interval=="15m" else "1mo"
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True, threads=False)
        if df.empty or len(df) < 30: return None
        close = df['Close']
        if isinstance(close, pd.DataFrame): close = close.iloc[:, 0]
        return float(rsi_wilder(close, 14).iloc[-1])
    except: return None

def bot_loop():
    send("✅ V4.8 LOGIQUE 45MIN DEPLOYÉ - Check 1min, alerte immédiate si changement, rappel 45min si même mouvement")
    while True:
        try:
            for coin in COINS:
                r15 = get_rsi(coin, "15m")
                r1h = get_rsi(coin, "1h")
                if r15 is None or r1h is None: continue

                if r15 < 30 and r1h < 35: current = "ACHAT"
                elif r15 > 70 and r1h > 65: current = "VENTE"
                else: current = "CALME"

                prev = last_state.get(coin)
                last_time = last_sent_time.get(coin)

                should_send = False
                # 1. Si ça change -> on envoie tout de suite
                if prev!= current:
                    should_send = True
                # 2. Si même état mais ça fait 45 min -> on rappelle
                elif last_time and datetime.now() - last_time > timedelta(minutes=45):
                    should_send = True
                # 3. Premier démarrage
                elif prev is None:
                    should_send = True

                if should_send:
                    if current == "ACHAT":
                        send(f"🟢 ACHAT FORT {coin}\n15m:{r15:.1f} 1h:{r1h:.1f} - CHANGEMENT IMMEDIAT")
                    elif current == "VENTE":
                        send(f"🔴 VENTE FORTE {coin}\n15m:{r15:.1f} 1h:{r1h:.1f} - CHANGEMENT IMMEDIAT")
                    else:
                        # Pour CALME on ne t'envoie plus toutes les minutes, seulement si changement ou rappel 45min
                        send(f"⏸️ {coin} Calme | 15m:{r15:.1f} 1h:{r1h:.1f}")

                    last_state[coin] = current
                    last_sent_time[coin] = datetime.now()

            time.sleep(60)
        except Exception as e:
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home(): return "V4.8 Live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
