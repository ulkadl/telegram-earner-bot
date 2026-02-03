from telegram.ext import Updater, CommandHandler
import sqlite3
import os

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

db = sqlite3.connect("users.db", check_same_thread=False)
cursor = db.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    points INTEGER DEFAULT 0,
    referrer INTEGER
)
""")
db.commit()

def start(update, context):
    user_id = update.effective_user.id
    ref = context.args[0] if context.args else None

    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        cursor.execute(
            "INSERT INTO users (user_id, referrer) VALUES (?,?)",
            (user_id, ref)
        )
        if ref:
            cursor.execute(
                "UPDATE users SET points = points + 10 WHERE user_id=?",
                (ref,)
            )
        db.commit()

    update.message.reply_text(
        "👋 Welcome!\n\n"
        "Earn points by inviting friends.\n"
        "10 points per referral!\n\n"
        f"Your referral link:\n"
        f"https://t.me/{context.bot.username}?start={user_id}"
    )

def balance(update, context):
    user_id = update.effective_user.id
    cursor.execute("SELECT points FROM users WHERE user_id=?", (user_id,))
    points = cursor.fetchone()[0]
    update.message.reply_text(f"💰 Your balance: {points} points")

def broadcast(update, context):
    if update.effective_user.id != ADMIN_ID:
        return
    msg = " ".join(context.args)
    cursor.execute("SELECT user_id FROM users")
    for u in cursor.fetchall():
        try:
            context.bot.send_message(u[0], msg)
        except:
            pass

updater = Updater(TOKEN, use_context=True)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("balance", balance))
dp.add_handler(CommandHandler("broadcast", broadcast))

updater.start_polling()
updater.idle()