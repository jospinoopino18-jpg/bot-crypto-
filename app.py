import os, threading
from flask import Flask
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.environ.get("8857935832:AAE8c7Xdqlb5o9vQmfSbpiH7anBMsLLSLts")  # tu mettras ton token dans Render

app = Flask(__name__)

@app.route("/")
def health():
    return "Bot en ligne !"

@app.route("/health")
def health2():
    return "OK"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut Jordan ! Le bot crypto est en ligne 🚀 24/24 sur Render !")

def run_bot():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.run_polling()

if __name__ == "__main__":
    threading.Thread(target=run_bot, daemon=True).start()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
