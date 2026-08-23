import yfinance as yf, time, requests
from datetime import datetime
from flask import Flask
import threading, os

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"
PAIRES = ["BTC-USD","ETH-USD","SOL-USD","DOGE-USD","SHIB-USD","AVAX-USD"]

dernier_signal, dernier_envoi, debut_calme = {}, {}, {}
app = Flask(__name__)
@app.route('/')
def home(): return "V6.3 DEBUG FORCE OK"

def calc_rsi(s, p=14):
    d=s.diff(); g=d.where(d>0,0).rolling(p).mean(); l=-d.where(d<0,0).rolling(p).mean()
    return 100-(100/(1+g/l))

def send(t):
    try: requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id":CHAT_ID,"text":t,"parse_mode":"Markdown"}, timeout=15)
    except Exception as e: print(f"send fail {e}")

def get_signal(sym):
    try:
        t = yf.Ticker(sym)
        df15 = t.history(period="2d", interval="15m", auto_adjust=True)
        df1h = t.history(period="7d", interval="1h", auto_adjust=True)
        if df15.empty or len(df15)<15: return f"ERR15 vide {sym}",0,0,0
        if df1h.empty or len(df1h)<14: return f"ERR1h vide {sym}",0,0,0
        r15=float(calc_rsi(df15['Close']).iloc[-1]); r1h=float(calc_rsi(df1h['Close']).iloc[-1]); price=float(df15['Close'].iloc[-1])
        if r15>60 and r1h>60: sig="ACHAT"
        elif r15<40 and r1h<40: sig="VENTE"
        else: sig="CALME"
        return sig, r15, r1h, price
    except Exception as e:
        return f"ERR {sym} {str(e)[:80]}",0,0,0

def run_bot():
    time.sleep(3)
    send(f"✅ *V6.3 FORCE START* {datetime.now().strftime('%H:%M')}\nJe force les 6 bilans maintenant...")
    for sym in PAIRES:
        sig,r15,r1h,price = get_signal(sym)
        if "ERR" in str(sig):
            send(f"⚠️ *{sym}* : {sig}\nJe retente...")
            time.sleep(3)
            sig,r15,r1h,price = get_signal(sym) # 2e tentative

        if "ERR" in str(sig):
            send(f"❌ *{sym} échoué*: {sig}")
        else:
            if sig=="ACHAT": send(f"🔵 *ACHAT {sym} - START*\n15m:{r15:.1f} 1h:{r1h:.1f} | {price:.2f}")
            elif sig=="VENTE": send(f"🔴 *VENTE {sym} - START*\n15m:{r15:.1f} 1h:{r1h:.1f} | {price:.2f}")
            else: send(f"⚪ *CALME {sym} - START*\n15m:{r15:.1f} 1h:{r1h:.1f} | {price:.2f}")
        dernier_signal[sym]=sig; dernier_envoi[sym]=datetime.now(); debut_calme[sym]=datetime.now()
        time.sleep(2)

    while True:
        for sym in PAIRES:
            try:
                sig,r15,r1h,price = get_signal(sym)
                if "ERR" in str(sig): continue
                now=datetime.now()
                if sig=="CALME":
                    if (now-debut_calme[sym]).total_seconds()>=900:
                        send(f"⚪ *CALME {sym}* depuis 15min\n15m:{r15:.1f} 1h:{r1h:.1f}")
                        debut_calme[sym]=now
                    continue
                debut_calme[sym]=now
                if dernier_signal.get(sym)!=sig or (now-dernier_envoi.get(sym, datetime.min)).total_seconds()>=2700:
                    send(f"{'🔵' if sig=='ACHAT' else '🔴'} *{sig} {sym}*\n15m:{r15:.1f} 1h:{r1h:.1f} | {price:.4f}")
                    dernier_signal[sym]=sig; dernier_envoi[sym]=now
            except: pass
            time.sleep(2)
        time.sleep(60)

threading.Thread(target=run_bot, daemon=True).start()
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))
