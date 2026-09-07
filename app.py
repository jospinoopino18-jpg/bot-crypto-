import requests, os
TOKEN = os.environ.get("8606332059:AAFhaW3DocdsC-0byBHhkLfaTy-UhktOBTo")
CHAT_ID = os.environ.get("7335134261")
print(f"TOKEN existe? {bool(TOKEN)}")
print(f"CHAT_ID: {CHAT_ID}")
url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
r = requests.post(url, data={"chat_id": CHAT_ID, "text": "TEST CONNEXION 🚀 Ca marche!"})
print(r.text)
