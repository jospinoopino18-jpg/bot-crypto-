import yfinance as yf
import pandas as pd
import time
import requests
from datetime import datetime
from flask import Flask
import threading

CAPITAL = 10.0
SEUIL_ACHAT = 60
SEUIL_VENTE = 40
RR = 2

PAIRES = ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "SHIB-USD", "AVAX-USD"]

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"

app = Flask(__name__)

@app.route('/')
def home():
    return f"V6 TENDANCE OK {datetime.now()}"

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def send_msg(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text}, timeout=10)
    except:
        pass

def run_bot():
    print("V6 LANCEE >60=ACHAT <40=VENTE")
    send_msg(f"✅ V6 démarré {datetime.now().strftime('%H:%M')} - Tendance 40/60")
    while True:
        for symbol in PAIRES:
            try:
                df15 = yf.download(symbol, period="2d", interval="15m", progress=False, auto_adjust=True)
                df1h = yf.download(symbol, period="7d", interval="1h", progress=False, auto_adjust=True)
                if df15.empty or df1h.empty: continue

                r15 = float(calc_rsi(df15['Close']).iloc[-1])
                r1h = float(calc_rsi(df1h['Close']).iloc[-1])
                price = float(df15['Close'].iloc[-1])

                if r15 > SEUIL_ACHAT and r1h > SEUIL_ACHAT:
                    msg = f"🔵 ACHAT {symbol}\n15m:{r15:.1f} 1h:{r1h:.1f}\nPrix:{price:.4f} SL-1% TP+2% RR 2/1"
                    print(msg)
                    send_msg(msg)
                elif r15 < SEUIL_VENTE and r1h < SEUIL_VENTE:
                    msg = f"🔴 VENTE {symbol}\n15m:{r15:.1f} 1h:{r1h:.1f}\nPrix:{price:.4f} SL+1% TP-2% RR 2/1"
                    print(msg)
                    send_msg(msg)
                else:
                    print(f"{datetime.now().strftime('%H:%M')} CALME {symbol} {r15:.1f}/{r1h:.1f}")

                time.sleep(3)
            except Exception as e:
                print(f"Err {symbol} {e}")
        time.sleep(900)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
