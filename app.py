import yfinance as yf
import pandas as pd
import time
import requests
from datetime import datetime
from flask import Flask
import threading
import os

CAPITAL = 10.0
RISQUE_PCT = 0.01
RR = 2
SEUIL_ACHAT = 60
SEUIL_VENTE = 40

PAIRES = {
    "BTC-USD": "BTCUSDm",
    "ETH-USD": "ETHUSDm",
    "SOL-USD": "SOLUSDm",
    "DOGE-USD": "DOGEUSDm",
    "SHIB-USD": "SHIBUSDm",
    "AVAX-USD": "AVAXUSDm"
}

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"

app = Flask(__name__)

@app.route('/')
def home():
    return "V6 TENDANCE OK"

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
    except Exception as e:
        print(f"Erreur Telegram: {e}")

def check_pair(symbol):
    try:
        df15 = yf.download(symbol, period="2d", interval="15m", progress=False)
        if df15.empty: return None
        df15['RSI'] = calc_rsi(df15['Close'])
        r15 = float(df15['RSI'].iloc[-1])
        df1h = yf.download(symbol, period="7d", interval="1h", progress=False)
        df1h['RSI'] = calc_rsi(df1h['Close'])
        r1h = float(df1h['RSI'].iloc[-1])
        price = float(df15['Close'].iloc[-1])
        if r15 > SEUIL_ACHAT and r1h > SEUIL_ACHAT:
            sens = "ACHAT"
            signal = f"🔵 ACHAT {symbol}"
        elif r15 < SEUIL_VENTE and r1h < SEUIL_VENTE:
            sens = "VENTE"
            signal = f"🔴 VENTE {symbol}"
        else:
            print(f"{datetime.now().strftime('%H:%M')} CALME {symbol} 15m:{r15:.1f} 1h:{r1h:.1f}")
            return None
        sl_dist = price * 0.01
        if sens == "ACHAT":
            sl = price - sl_dist
            tp = price + sl_dist * RR
        else:
            sl = price + sl_dist
            tp = price - sl_dist * RR
        msg = (f"{signal}\n15m:{r15:.1f} 1h:{r1h:.1f} (tendance)\n"
               f"Prix:{price:.4f} SL:{sl:.2f} TP:{tp:.2f}\n"
               f"10$ -> Risque 0.10$ Gain 0.20$ RR {RR}/1")
        return msg
    except Exception as e:
        print(f"Erreur {symbol}: {e}")
        return None

def run_bot():
    print("V6 TENDANCE lancée - 40/60 - >60=ACHAT <40=VENTE", flush=True)
    send_msg(f"✅ V6 TENDANCE démarré {datetime.now().strftime('%H:%M')}")
    while True:
        for sym in PAIRES:
            msg = check_pair(sym)
            if msg:
                print(msg, flush=True)
                send_msg(msg)
            time.sleep(3)
        time.sleep(900)

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
