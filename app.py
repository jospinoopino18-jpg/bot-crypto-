import yfinance as yf
import pandas as pd
import time
import requests
from datetime import datetime

# === CONFIG V6 TENDANCE ===
CAPITAL = 10.0
RISQUE_PCT = 0.01  # 1%
RR = 2  # 2/1

PAIRES = {
    "BTC-USD": "BTCUSDm",
    "ETH-USD": "ETHUSDm", 
    "SOL-USD": "SOLUSDm",
    "DOGE-USD": "DOGEUSDm",
    "SHIB-USD": "SHIBUSDm",
    "AVAX-USD": "AVAXUSDm"
}

# SEUILS TENDANCE PURE 40/60
SEUIL_ACHAT = 60  # >60 = ACHAT (on suit la pompe)
SEUIL_VENTE = 40  # <40 = VENTE (on suit la chute)

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def send_msg(text):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    try:
        requests.post(url, data={"chat_id": CHAT_ID, "text": text})
    except:
        print(text)

def check_pair(symbol):
    try:
        # 15m
        df15 = yf.download(symbol, period="2d", interval="15m", progress=False)
        df15['RSI'] = calc_rsi(df15['Close'])
        r15 = float(df15['RSI'].iloc[-1])
        
        # 1h
        df1h = yf.download(symbol, period="7d", interval="1h", progress=False)
        df1h['RSI'] = calc_rsi(df1h['Close'])
        r1h = float(df1h['RSI'].iloc[-1])
        
        price = float(df15['Close'].iloc[-1])
        
        # === LOGIQUE V6 TENDANCE (TA STRATÉGIE) ===
        if r15 > SEUIL_ACHAT and r1h > SEUIL_ACHAT:
            signal = f"🔵 ACHAT {symbol}"
            sens = "ACHAT"
        elif r15 < SEUIL_VENTE and r1h < SEUIL_VENTE:
            signal = f"🔴 VENTE {symbol}"
            sens = "VENTE"
        else:
            signal = f"⚪ CALME {symbol}"
            sens = "CALME"
        
        # Calcul SL/TP pour 10$ avec 1% et RR 2/1
        risque_dollar = CAPITAL * RISQUE_PCT  # 0.10$
        
        if "BTC" in symbol:
            sl_dist = 100
            tp_dist = 200
            lot = 0.01
        elif "ETH" in symbol:
            sl_dist = 10
            tp_dist = 20
            lot = 0.01
        else: # DOGE, SHIB parfait pour 10$
            sl_dist = price * 0.01  # 1% de distance
            tp_dist = sl_dist * RR
            lot = 0.01

        if sens == "ACHAT":
            sl = price - sl_dist
            tp = price + tp_dist
        elif sens == "VENTE":
            sl = price + sl_dist
            tp = price - tp_dist
        else:
            sl = tp = 0

        # Message final
        if sens != "CALME":
            msg = (f"{signal}\n"
                   f"15m:{r15:.1f} 1h:{r1h:.1f} (tendance)\n"
                   f"Prix:{price:.4f} Lot:{lot} SL:{sl:.2f} TP:{tp:.2f}\n"
                   f"Risque: {risque_dollar:.2f}$ | Gain: {risque_dollar*RR:.2f}$ | RR {RR}/1")
            return msg
        else:
            return f"{signal}\n15m:{r15:.1f} 1h:{r1h:.1f} (tendance)"

    except Exception as e:
        return f"Erreur {symbol}: {e}"

# === BOUCLE ===
print("V6 TENDANCE lancée - 40/60 - >60=ACHAT <40=VENTE")
while True:
    for sym in PAIRES:
        msg = check_pair(sym)
        if "ACHAT" in msg or "VENTE" in msg:
            if "CALME" not in msg:
                # Envoie seulement si >60 ou <40 sur les 2 TF
                print(f"{datetime.now().strftime('%H:%M')} {msg}")
                send_msg(f"{datetime.now().strftime('%H:%M')} {msg}")
        time.sleep(2)
    print(f"--- Scan {datetime.now().strftime('%H:%M:%S')} terminé, attente 15min ---")
    time.sleep(900) # 15min
    send_msg(f"Test V6 OK - {datetime.now().strftime('%H:%M')} - Bot en ligne")
