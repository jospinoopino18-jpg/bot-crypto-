import requests, time
TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"
CHAT_ID = "7335134261"

# Test direct immédiat
r = requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage", data={"chat_id": CHAT_ID, "text": "BOT REPLIT OK 🚀"})
print(r.text)
print("Si tu vois ok:true ci-dessus, regarde Telegram !")

# Boucle pour garder Replit allumé
while True:
    time.sleep(60)
