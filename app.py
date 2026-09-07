import yfinance as yf, pandas as pd, ta, time, requests, threading, os
from flask import Flask

# --- METS TES INFOS ICI ---
TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "7335134261")
# --------------------------

PAIRES = ["BTC-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD","DOGE-USD"]
app = Flask(__name__)

def send_telegram(m):
    try:
        print(m)
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": m}, timeout=10)
    except Exception as e:
        print(f"Erreur telegram: {e}")

def check(p, tf):
    try:
        df = yf.download(p, period="3d", interval=tf, progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if len(df) < 50:
            return None
        df['ema20'] = ta.trend.EMAIndicator(df['Close'], 20).ema_indicator()
        df['ema50'] = ta.trend.EMAIndicator(df['Close'], 50).ema_indicator()
        df['rsi'] = ta.momentum.RSIIndicator(df['Close'], 14).rsi()
        df['adx'] = ta.trend.ADXIndicator(df['High'], df['Low'], df['Close'], 14).adx()
        last = df.iloc[-1]
        if last['adx'] < 20:
            return None
        if last['ema20'] > last['ema50'] and 50 < last['rsi'] < 70:
            return f"🟢 BUY {p} {tf} | RSI {last['rsi']:.1f} | ADX {last['adx']:.1f} | EMA20>{'EMA50'}"
        if last['ema20'] < last['ema50'] and 30 < last['rsi'] < 50:
            return f"🔴 SELL {p} {tf} | RSI {last['rsi']:.1f} | ADX {last['adx']:.1f} | EMA20<{'EMA50'}"
    except Exception as e:
        print(f"Erreur check {p} {tf}: {e}")
        return None

def bot_loop():
    send_telegram("BOT ANALYSEUR LANCE 🚀\nScan 15m + 1h toutes les 60 sec")
    dernier_no_signal = 0
    while True:
        signal_trouve = False
        for pair in PAIRES:
            for tf in ["15m", "1h"]:
                s = check(pair, tf)
                if s:
                    send_telegram(s)
                    signal_trouve = True
                time.sleep(2)
        if not signal_trouve and time.time() - dernier_no_signal > 900:
            send_telegram("⏳ Aucun coin aligné en 15m+1h - marché calme")
            dernier_no_signal = time.time()
        time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route('/')
def home():
    return "BOT ACTIF - Analyseur en cours"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
