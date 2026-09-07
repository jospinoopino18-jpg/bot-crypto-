import requests, os, time, threading
from flask import Flask
TOKEN=os.environ.get("8606332059:AAFhaW3DocdsC-0byBHhkLfaTy-UhktOBTo")
CHAT_ID=os.environ.get("7335134261")
app=Flask(__name__)
def bot_loop():
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",data={"chat_id":CHAT_ID,"text":"BOT ANALYSEUR RELANCE 🚀 Enfin!"},timeout=10)
    except Exception as e:
        print(e)
    while True:
        time.sleep(60)
threading.Thread(target=bot_loop,daemon=True).start()
@app.route('/')
def home(): return "BOT ACTIF"
if __name__=='__main__':
    app.run(host='0.0.0.0',port=int(os.environ.get("PORT",10000)))
