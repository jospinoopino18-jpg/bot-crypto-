!pip install yfinance ta -q
import yfinance as yf, pandas as pd, ta, time, requests
from datetime import datetime

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
PAIRES = ["BTC-USD","SOL-USD","BNB-USD","XRP-USD","ADA-USD","DOGE-USD"]

def send_telegram(m):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":m}, timeout=5)
    except: pass

def check(p,tf):
    try:
        df=yf.download(p,period="3d",interval=tf,progress=False)
        if len(df)<50: return None
        df['ema20']=ta.trend.EMAIndicator(df['Close'],20).ema_indicator()
        df['ema50']=ta.trend.EMAIndicator(df['Close'],50).ema_indicator()
        df['rsi']=ta.momentum.RSIIndicator(df['Close'],14).rsi()
        df['adx']=ta.trend.ADXIndicator(df['High'],df['Low'],df['Close'],14).adx()
        last=df.iloc[-1]
        if last['adx']<20: return None
        if last['ema20']>last['ema50'] and 50<last['rsi']<70:
            return f"BUY {p} {tf} RSI {last['rsi']:.1f}"
        if last['ema20']<last['ema50'] and 30<last['rsi']<50:
            return f"SELL {p} {tf} RSI {last['rsi']:.1f}"
    except: return None
    return None

send_telegram("BOT CRYPTO LANCE")
print("BOT LANCE - Attente scan...")

while True:
    for pair in PAIRES:
        for tf in ["15m","1h"]:
            s=check(pair,tf)
            if s:
                msg=f"{'🟢' if 'BUY' in s else '🔴'} {s}"
                print(msg)
                send_telegram(msg)
    print(f"{datetime.now().strftime('%H:%M')} Scan OK")
    time.sleep(60)
