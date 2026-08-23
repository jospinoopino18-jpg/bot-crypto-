import yfinance as yf
import time
import requests
from datetime import datetime
from flask import Flask
import threading
import os

# --- CONFIG ---
TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"

PAIRES = ["BTC-USD", "ETH-USD", "SOL-USD", "DOGE-USD", "SHIB-USD", "AVAX-USD"]
SEUIL_ACHAT = 60
SEUIL_VENTE = 40

# Mémoire
dernier_signal = {} # ACHAT / VENTE
dernier_envoi = {} # datetime
debut_calme = {} # datetime debut calme

app = Flask(__name__)
@app.route('/')
def home():
    return "V6 TENDANCE 40/60 OK - 1min"

def calc_rsi(series, period=14):
    delta = series.diff()
    gain = delta.where(delta > 0, 0).rolling(window=period).mean()
    loss = -delta.where(delta < 0, 0).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def send_telegram(text):
    try:
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}, timeout=10)
    except Exception as e:
        print(f"Erreur Telegram: {e}")

def run_bot():
    print("V6 TENDANCE 40/60 INVERSE - CHECK 1MIN - RAPPEL 45MIN - CALME 15MIN", flush=True)
    send_telegram(f"✅ *V6 TENDANCE démarré* {datetime.now().strftime('%H:%M')}\nCheck 1min | Rappel 45min | Calme 15min")

    while True:
        for sym in PAIRES:
            try:
                # Data
                df15 = yf.download(sym, period="2d", interval="15m", progress=False, auto_adjust=True)
                df1h = yf.download(sym, period="7d", interval="1h", progress=False, auto_adjust=True)
                if df15.empty or df1h.empty:
                    continue

                r15 = float(calc_rsi(df15['Close']).iloc[-1])
                r1h = float(calc_rsi(df1h['Close']).iloc[-1])
                price = float(df15['Close'].iloc[-1])

                # Logique tendance
                signal_actuel = None
                if r15 > SEUIL_ACHAT and r1h > SEUIL_ACHAT:
                    signal_actuel = "ACHAT"
                elif r15 < SEUIL_VENTE and r1h < SEUIL_VENTE:
                    signal_actuel = "VENTE"

                maintenant = datetime.now()

                # CAS CALME
                if signal_actuel is None:
                    print(f"{maintenant.strftime('%H:%M')} CALME {sym} 15m:{r15:.1f} 1h:{r1h:.1f}", flush=True)
                    if sym not in debut_calme:
                        debut_calme[sym] = maintenant
                    else:
                        duree_calme = (maintenant - debut_calme[sym]).total_seconds()
                        if duree_calme > 900: # 15 min = 900 sec
                            msg = f"⚪ *CALME {sym}* depuis 15min\n15m:{r15:.1f} 1h:{r1h:.1f} | Prix: {price:.2f}"
                            send_telegram(msg)
                            debut_calme[sym] = maintenant # reset
                    continue
                else:
                    # Plus calme, on efface le compteur calme
                    debut_calme.pop(sym, None)

                # CAS SIGNAL
                dernier = dernier_signal.get(sym)
                heure_dernier = dernier_envoi.get(sym)

                doit_envoyer = False
                if dernier!= signal_actuel:
                    doit_envoyer = True # changement immédiat
                elif heure_dernier is None or (maintenant - heure_dernier).total_seconds() > 2700: # 45 min
                    doit_envoyer = True # rappel 45min

                if doit_envoyer:
                    emoji = "🔵" if signal_actuel == "ACHAT" else "🔴"
                    msg = (f"{emoji} *{signal_actuel} {sym}*\n"
                           f"15m:{r15:.1f} 1h:{r1h:.1f} (tendance)\n"
                           f"Prix: {price:.4f} | SL 1% TP 2% RR2")
                    print(msg, flush=True)
                    send_telegram(msg)
                    dernier_signal[sym] = signal_actuel
                    dernier_envoi[sym] = maintenant

            except Exception as e:
                print(f"Erreur {sym}: {e}", flush=True)
            time.sleep(2) # petite pause entre paires
        time.sleep(60) # CHECK TOUTES LES 1 MINUTE

threading.Thread(target=run_bot, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
