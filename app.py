from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot crypto en ligne ! Le bot fonctionne."

@app.route('/price')
def price():
    return {"BTC": "en cours", "status": "OK"}

if __name__ == '__main__':
    app.run()
