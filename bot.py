import telebot
from telebot import types
import sqlite3
import threading
from flask import Flask

# ======================
# WEB (для Render)
# ======================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running 🚀"

def run_web():
    app.run(host="0.0.0.0", port=10000)


# ======================
# TOKEN
# ======================

TOKEN = "8906331404:AAF5oaTI7zcoknNrmqzBlS-_VX_eCoPT0LA"  # ← встав свій токен

bot = telebot.TeleBot(TOKEN)


# ======================
# CONFIG
# ======================

ADMIN_PASSWORD = "856243"

admin_mode = set()
user_lang = {}
bot_active = True


# ======================
# DATABASE
# ======================

conn = sqlite3.connect("sales.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS leads(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER
)
""")

conn.commit()


def add_user(user):
    cur.execute(
        "INSERT OR IGNORE INTO users VALUES (?,?)",
        (user.id, user.username)
    )
    conn.commit()


def add_lead(uid):
    cur.execute(
        "INSERT INTO leads(user_id) VALUES(?)",
        (uid,)
    )
    conn.commit()


def stats():
    cur.execute("SELECT COUNT(*) FROM users")
    u = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM leads")
    l = cur.fetchone()[0]

    return u, l


# ======================
# TEXTS
# ======================

def text(uid, key):
    lang = user_lang.get(uid, "ua")

    data = {
        "start": {
            "ua": "👋 Вітаю! Обери мову",
            "en": "👋 Welcome!"
        },
        "menu": {
            "ua": "👇 Обери дію",
            "en": "👇 Choose action"
        },
        "info": {
            "ua": "🔥 Telegram бот для бізнесу\n\n✅ Автоматизація\n✅ Заявки\n✅ CRM\n✅ 24/7",
            "en": "🔥 Telegram business bot\n\n✅ Automation\n✅ Leads\n✅ CRM\n✅ 24/7"
        },
        "price": {
            "ua": "💰 Ціна:\n\nБазовий $30\nСтандарт $70\nБізнес $150",
            "en": "💰 Price:\n\nBasic $30\nStandard $70\nBusiness $150"
        },
        "order": {
            "ua": "📦 Напиши: ХОЧУ БОТА",
            "en": "📦 Write: I WANT BOT"
        },
        "contact": {
            "ua": "📞 @Life_Industryl",
            "en": "📞 @Life_Industryl"
        }
    }

    return data[key][lang]


# ======================
# START
# ======================

@bot.message_handler(commands=["start"])
def start(message):
    add_user(message.from_user)

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🇺🇦 Українська", "🇬🇧 English")

    bot.send_message(
        message.chat.id,
        text(message.chat.id, "start"),
        reply_markup=kb
    )


# ======================
# LANGUAGE
# ======================

@bot.message_handler(func=lambda m: m.text in ["🇺🇦 Українська", "🇬🇧 English"])
def language(message):

    if "Українська" in message.text:
        user_lang[message.chat.id] = "ua"
    else:
        user_lang[message.chat.id] = "en"

    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🤖 Info", "💰 Price")
    kb.add("📦 Order", "📞 Contact")

    bot.send_message(
        message.chat.id,
        text(message.chat.id, "menu"),
        reply_markup=kb
    )


# ======================
# ADMIN
# ======================

@bot.message_handler(commands=["admin"])
def admin(message):
    try:
        pwd = message.text.split()[1]

        if pwd == ADMIN_PASSWORD:
            admin_mode.add(message.chat.id)
            bot.send_message(message.chat.id, "🔐 ADMIN ON")
        else:
            bot.send_message(message.chat.id, "❌ Wrong password")

    except:
        bot.send_message(message.chat.id, "/admin password")


# ======================
# MAIN HANDLER
# ======================

@bot.message_handler(func=lambda m: True)
def handler(message):

    global bot_active

    if not bot_active:
        return

    add_lead(message.chat.id)

    t = message.text

    if t == "🤖 Info":
        bot.send_message(message.chat.id, text(message.chat.id, "info"))

    elif t == "💰 Price":
        bot.send_message(message.chat.id, text(message.chat.id, "price"))

    elif t == "📦 Order":
        bot.send_message(message.chat.id, text(message.chat.id, "order"))

    elif t == "📞 Contact":
        bot.send_message(message.chat.id, text(message.chat.id, "contact"))

    elif message.chat.id in admin_mode:
        if t == "📊 Stats":
            u, l = stats()
            bot.send_message(message.chat.id, f"Users: {u}\nLeads: {l}")


# ======================
# RUN
# ======================

if __name__ == "__main__":
    threading.Thread(target=run_web).start()

    print("🚀 Bot started...")
    bot.infinity_polling()
