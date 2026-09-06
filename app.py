# Bot complet Traders Family V4 - 4 fonctions
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import asyncio

TOKEN = "8857935832:AAH37acQPQwjPkOcwpuNrryRm5lQSdJFkS8"  # Colle ton NOUVEAU token ici
CANAL_ID = "@eurusd_pips"
CANAL_USERNAME = "eurusd_pips"

# 1. ACCUEIL AUTO
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

# 2. RÉPONSE AUTO
async def auto_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    user = update.message.from_user.first_name
    
    # Anti-spam simple
    spam_words = ["xxx", "porno", "gagne 1000", "crypto doublé", "investis 10"]
    if any(w in text for w in spam_words):
        await update.message.delete()
        return

    if "signaux" in text or "signal" in text or "us30" in text:
        await update.message.reply_text(f"{user}, 📈 SIGNAL DU JOUR:\nUS30 BUY 53225\nTP1 53250 ✅\nTP2 53300\nTP3 53400\nSL 53150\nDétails: @{CANAL_USERNAME}")
    elif "bonjour" in text or "salut" in text or "hello" in text:
        await update.message.reply_text(f"Salut {user} ! Prêt pour les profits ? Tape /signaux")
    elif "merci" in text:
        await update.message.reply_text(f"De rien {user} 🙏 On encaisse ensemble!")
    else:
        await update.message.reply_text("Tape /signaux pour les signaux ou /canal pour rejoindre 👉 @eurusd_pips")

# 3. BIENVENUE NOUVEAUX MEMBRES
async def welcome_new(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(
            f"Bienvenue {member.first_name} 👑\n"
            f"Tu as rejoint les meilleurs !\n"
            f"3 TP HIT aujourd'hui +10.91$\n"
            f"Lis les règles épinglées et tape /signaux"
        )

# Commandes
async def canal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👉 Rejoins ici: https://t.me/eurusd_pips\n📈 5000+ traders actifs")

async def aide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Support: @ton_username_admin\nSignaux tous les jours 08h & 15h GMT")

# 4. POST AUTO DANS LE CANAL (toutes les 6h)
async def auto_post_loop(app):
    await asyncio.sleep(10) # attend démarrage
    while True:
        try:
            await app.bot.send_message(
                chat_id=CANAL_ID,
                text="🔥 SIGNAL LIVE - TRADERS FAMILY V4 🔥\n\n"
                     "US30 BUY NOW 53225\n"
                     "TP1: 53250 | TP2: 53300 | TP3: 53400\n"
                     "SL: 53150\n\n"
                     "✅ 87% Win Rate | 3 TP aujourd'hui\n"
                     "👉 @eurusd_pips"
            )
        except Exception as e:
            print(f"Erreur post auto: {e}")
        await asyncio.sleep(21600) # 6 heures

# Lancement
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("signaux", auto_reply))
app.add_handler(CommandHandler("canal", canal))
app.add_handler(CommandHandler("aide", aide))
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome_new))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_reply))

# Active le post auto
app.job_queue.run_once(lambda c: asyncio.create_task(auto_post_loop(app)), 1)

print("Bot @bot_trading_v4_bot lancé 24/24 avec 4 fonctions!")
app.run_polling()
