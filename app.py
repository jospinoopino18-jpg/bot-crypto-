from flask import Flask
import requests, threading, time, yfinance as yf
import pandas_ta as ta
from datetime import datetime

app = Flask(__name__)

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
COINS = ["BTC-USD", "ETH-USD", "SOL-USD", "BNB-USD", "XRP-USD", "DOGE-USD"]

dernier_signal_envoye = {}
last_no_signal = 0

def send_telegram(msg):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=10)
        print(f"TELEGRAM: {msg}")
    except Exception as e:
        print(f"Erreur TG: {e}")

def get_rsi_yf(symbol, interval):
    try:
        # 15m = 5 jours de données, 1h = 1 mois
        period = "5d" if interval == "15m" else "1mo"
        tf = "15m" if interval == "15m" else "1h"
        df = yf.download(symbol, period=period, interval=tf, progress=False, auto_adjust=True)
        if len(df) < 20: return None
        df['RSI'] = ta.rsi(df['Close'], length=14)
        return float(df['RSI'].iloc[-1])
    except Exception as e:
        print(f"Erreur RSI {symbol} {interval}: {e}")
        return None

def bot_loop():
    global last_no_signal
    send_telegram("✅ Bot V4.3 CORRIGÉ - Vrai RSI yfinance lancé")
    while True:
        signal_trouve = False
        for coin in COINS:
            rsi_15m = get_rsi_yf(coin, "15m")
            rsi_1h = get_rsi_yf(coin, "1h")
            print(f"{coin} -> 15m:{rsi_15m} | 1h:{rsi_1h}")
            if rsi_15m is None or rsi_1h is None: continue

            # SEUILS 60 / 40 comme ton MT5
            type_signal = None
            if rsi_15m > 60 and rsi_1h > 60: type_signal = "BUY"
            elif rsi_15m < 40 and rsi_1h < 40: type_signal = "SELL"

            if type_signal:
                cle = f"{coin}_{type_signal}"
                if cle in dernier_signal_envoye and time.time() - dernier_signal_envoye[cle] < 2700:
                    signal_trouve = True
                    continue
                signal_trouve = True
                dernier_signal_envoye[cle] = time.time()
                if type_signal == "BUY":
                    send_telegram(f"🚀 STRONG BUY {coin}\n15m: {rsi_15m:.1f} | 1h: {rsi_1h:.1f}\n{datetime.now().strftime('%H:%M')}")
                else:
                    send_telegram(f"🔻 STRONG SELL {coin}\n15m: {rsi_15m:.1f} | 1h: {rsi_1h:.1f}\n{datetime.now().strftime('%H:%M')}")

        if not signal_trouve:
            if time.time() - last_no_signal > 900:
                send_telegram(f"⏳ Calme plat - aucun aligné 15m+1h {datetime.now().strftime('%H:%M')}")
                last_no_signal = time.time()
        time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home(): return "Bot V4.3 Live - yfinance"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
