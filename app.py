import yfinance as yf, pandas as pd, ta, time, requests, threading
from flask import Flask
from datetime import datetime
import os

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
PAIRES = ["BTC-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD","DOGE-USD"]

app = Flask(__name__)

def send_telegram(m):
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m}, timeout=10)
    except: pass

def check(p,tf):
    try:
        df=yf.download(p,period="3d",interval=tf,progress=False, auto_adjust=True)
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        if len(df)<50:
            return None
        df['ema20']=ta.trend.EMAIndicator(df['Close'],20).ema_indicator()
        df['ema50']=ta.trend.EMAIndicator(df['Close'],50).ema_indicator()
        df['rsi']=ta.momentum.RSIIndicator(df['Close'],14).rsi()
        df['adx']=ta.trend.ADXIndicator(df['High'],df['Low'],df['Close'],14).adx()
        last=df.iloc[-1]
        if last['adx']<20:
            return None
        if last['ema20']>last['ema50'] and 50<last['rsi']<70:
            return f"🟢 BUY {p} {tf} RSI {last['rsi']:.1f}"
        if last['ema20']<last['ema50'] and 30<last['rsi']<50:
            return f"🔴 SELL {p} {tf} RSI {last['rsi']:.1f}"
    except:
        return None

def bot_loop():
    send_telegram("🚀 BOT CRYPTO OPINO LANCE - EMA20/50 + RSI + ADX")
    while True:
        for pair in PAIRES:
            for tf in ["15m","1h"]:
                s=check(pair,tf)
                if s:
                    send_telegram(s)
        time.sleep(60)

threading.Thread(target=bot_loop, daemon=True).start()

@app.route('/')
def home():
    return f"BOT ACTIF - {datetime.now().strftime('%H:%M:%S')}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
