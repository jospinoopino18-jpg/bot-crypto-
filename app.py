from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

# ========== CONFIG ==========
TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"  # TON TOKEN ACTUEL POUR TEST - CHANGE APRES
CANAL_ID = "@eurusd_pips"  # Si ça marche pas mets: -100xxxxxxxxxx
# ============================

# 1. ACCUEIL AUTO QUAND ON LANCE /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 Bienvenue chez TRADERS FAMILY V4 👑\n\n"
        "🔥 +10.91 USD aujourd'hui - 3 TP HIT\n"
        "📊 Signaux US30 | EUR/USD | GBP/USD\n"
        "⏰ 2-3 signaux par jour\n\n"
        "👇 MENU:\n"
        "/signaux - Voir signaux du jour\n"
        "/canal - Lien du canal\n"
        "/aide - Support\n\n"
        "Rejoins 5000+ traders: https://t.me/eurusd_pips"
    )

async def canal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👉 Rejoins ici: https://t.me/eurusd_pips\n📈 5000+ traders actifs")

async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Support: Contacte l'admin du canal @eurusd_pips\nSignaux tous les jours 08h & 15h GMT")

# 2. REPONSE AUTO A TOUS LES MESSAGES
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user = update.message.from_user.first_name

    # ANTI-SPAM
    spam_words = ["xxx", "porno", "gagne 1000", "crypto double", "investis 10", "http://", "t.me/"]
    if any(w in text for w in spam_words):
        if update.message.chat.type != "private": # supprime que dans groupe/canal
            try:
                await update.message.delete()
                await context.bot.send_message(chat_id=update.message.chat_id, text=f"🚫 Message spam de {user} supprimé")
            except:
                pass
        return

    if "signaux" in text or "signal" in text or "us30" in text or "eurusd" in text:
        await update.message.reply_text(
            f"{user}, 📈 SIGNAL DU JOUR:\n\n"
            f"US30 BUY 53225\n"
            f"TP1 53250 ✅ HIT\n"
            f"TP2 53300\n"
            f"TP3 53400\n"
            f"SL 53150\n\n"
            f"Détails complets: @eurusd_pips"
        )
    elif "bonjour" in text or "salut" in text or "hello" in text or "cc" in text:
        await update.message.reply_text(f"Salut {user} ! 👋 Prêt pour les profits ? Tape /signaux")
    elif "merci" in text:
        await update.message.reply_text(f"De rien {user} 🙏 On encaisse ensemble!")
    else:
        await update.message.reply_text("Tape /signaux pour les signaux ou /canal pour rejoindre 👉 @eurusd_pips")

# 3. BIENVENUE NOUVEAUX MEMBRES
async def welcome_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        await update.message.reply_text(
            f"Bienvenue {member.first_name} 👑\n"
            f"Tu as rejoint les meilleurs !\n"
            f"3 TP HIT aujourd'hui +10.91$\n"
            f"Lis les règles épinglées et tape /signaux"
        )

# 4. POST AUTO DANS LE CANAL TOUTES LES 6H
async def post_dans_canal(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(
            chat_id=CANAL_ID,
            text="🔥 SIGNAL LIVE - TRADERS FAMILY V4 🔥\n\n"
                 "US30 BUY NOW 53225\n"
                 "TP1: 53250 | TP2: 53300 | TP3: 53400\n"
                 "SL: 53150\n\n"
                 "✅ 87% Win Rate | 3 TP aujourd'hui\n"
                 "👉 @eurusd_pips\n\n"
                 "Pour recevoir en privé: /signaux"
        )
        print("Message posté dans le canal avec succès!")
    except Exception as e:
        print(f"ERREUR post canal: {e}")
        print("VERIFIE: Le bot est-il admin dans le canal ?")

# LANCEMENT DU BOT
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("signaux", auto_reply))
    app.add_handler(CommandHandler("canal", canal))
    app.add_handler(CommandHandler("aide", aide))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

    # Active le post auto toutes les 6 heures (21600 secondes)
    # Premier post dans 10 secondes après démarrage
    app.job_queue.run_once(post_dans_canal, 10)
    app.job_queue.run_repeating(post_dans_canal, interval=21600, first=21600)

    print("Bot @bot_trading_v4_bot lancé 24/24 !")
    app.run_polling()

if __name__ == "__main__":
    main()
