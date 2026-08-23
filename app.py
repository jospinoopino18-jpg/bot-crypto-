from flask import Flask
import requests, threading, time, yfinance as yf
from datetime import datetime

app = Flask(__name__)
TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8" # CHANGE APRES AVOIR REVOQUE
CHAT_ID = "7335134261"
COINS = ["BTC-USD", "ETH-USD", "SOL-USD", "AVAX-USD", "DOGE-USD", "SHIB-USD"]

def send(msg):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": msg}, timeout=15)
    except Exception as e: print(e)

def rsi_calc(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_rsi(symbol, interval):
    try:
        period = "5d" if interval=="15m" else "1mo"
        df = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
        if len(df) < 30: return None
        df['RSI'] = rsi_calc(df['Close'], 14)
        return float(df['RSI'].iloc[-1])
    except: return None

def bot_loop():
    send("✅ BOT V4.6 STRATÉGIE ALIGNÉE DEPLOYÉ - RSI 15m + 1h sans pandas_ta")
    while True:
        try:
            for coin in COINS:
                r15 = get_rsi(coin, "15m")
                r1h = get_rsi(coin, "1h")
                if r15 is None or r1h is None:
                    send(f"⚠️ {coin} données indispo")
                    continue

                # TA STRATEGIE ALIGNEE
                if r15 < 30 and r1h < 35:
                    send(f"🟢 ACHAT FORT {coin}\n15m RSI: {r15:.1f}\n1h RSI: {r1h:.1f}\nSurvente alignée !")
                elif r15 > 70 and r1h > 65:
                    send(f"🔴 VENTE FORT {coin}\n15m RSI: {r15:.1f}\n1h RSI: {r1h:.1f}\nSurachat aligné !")
                else:
                    send(f"⏸️ {coin} Calme plat (mais nouveau code !) | 15m:{r15:.1f} 1h:{r1h:.1f}")

            time.sleep(900)
        except Exception as e:
            send(f"Loop err: {e}")
            time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route("/")
def home(): return "Bot V4.6 Strategie Live"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
