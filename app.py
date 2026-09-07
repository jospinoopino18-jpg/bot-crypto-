import telebot
TOKEN = "8857935832:AAGcA6N7JNzeKLW2cjL_RrcNx_gPTTUItKw"
bot = telebot.TeleBot(TOKEN)

CANAL = "@ton_nom_de_canal" # ex: @crypto_douala

@bot.message_handler(func=lambda m: True)
def repondre(message):
    bot.reply_to(message, "Salut, j'ai bien reçu ton message !")
    bot.send_message(CANAL, f"Nouveau message de {message.from_user.first_name}: {message.text}")

bot.infinity_polling()
