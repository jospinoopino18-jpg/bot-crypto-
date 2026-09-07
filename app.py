import requests, time
TOKEN = "8606332059:AAFhaW3DocdsC-0byBHhkLfaTy-UhktOBTo"
CHAT_ID = "7335134261"

# Test direct immédiat
r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": "BOT REPLIT OK 🚀"})
print(r.text)
print("Si tu vois ok:true ci-dessus, regarde Telegram !")

# Boucle pour garder Replit allumé
while True:
    time.sleep(60)
