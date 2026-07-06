import telebot
from telebot import types
import sqlite3
import os
import threading

# ======================
# 🔐 CONFIG
# ======================

TOKEN = "8906331404:AAGgRbXZT4hc9p8RoIQzAqNhSeQJgIAoAJA"
bot = telebot.TeleBot(TOKEN)

ADMIN_PASSWORD = "856243"
admin_mode = set()
waiting_broadcast = set()
user_lang = {}
bot_active = True

# ======================
# 🌐 FAKE WEB SERVER (RENDER FIX)
# ======================

app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running 🚀"

def run_web():
    app.run(host="0.0.0.0", port=10000)

threading.Thread(target=run_web).start()

# ======================
# 🗄 DATABASE
# ======================

conn = sqlite3.connect("sales.db", check_same_thread=False)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT
)
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER
)
""")

conn.commit()

# ======================
# DB FUNCTIONS
# ======================

def add_user(user):
    cur.execute(
        "INSERT OR IGNORE INTO users (id, username) VALUES (?, ?)",
        (user.id, user.username)
    )
    conn.commit()


def add_lead(user_id):
    cur.execute("INSERT INTO leads (user_id) VALUES (?)", (user_id,))
    conn.commit()


def count_users():
    cur.execute("SELECT COUNT(*) FROM users")
    return cur.fetchone()[0]


def count_leads():
    cur.execute("SELECT COUNT(*) FROM leads")
    return cur.fetchone()[0]


def get_users():
    cur.execute("SELECT id FROM users")
    return [x[0] for x in cur.fetchall()]

# ======================
# 🌍 LANGUAGE
# ======================

def get_text(uid, key):
    lang = user_lang.get(uid, "ua")

    texts = {
        "start": {
            "ua": "👋 Вітаю! Обери мову:",
            "en": "👋 Welcome! Choose language:"
        },
        "menu": {
            "ua": "👇 Обери дію:",
            "en": "👇 Choose option:"
        },
        "info": {
            "ua": "🔥 Ви отримаєте:\n"
                  "- Telegram бот під бізнес\n"
                  "- Автоматизацію клієнтів\n"
                  "- 24/7 відповіді\n"
                  "- Збір заявок\n"
                  "- CRM система\n"
                  "- Хостинг (сервер)\n\n"
                  "💡 Бот працює 24/7 на сервері",
            "en": "🔥 You get:\n"
                  "- Telegram business bot\n"
                  "- Automation\n"
                  "- 24/7 replies\n"
                  "- Lead collection\n"
                  "- CRM system\n"
                  "- Hosting (server)\n\n"
                  "💡 Bot works 24/7"
        },
        "price": {
            "ua": "💰 Ціна:\n"
                  "- Базовий: $30\n"
                  "- Стандарт: $70\n"
                  "- Бізнес: $150",
            "en": "💰 Price:\n"
                  "- Basic: $30\n"
                  "- Standard: $70\n"
                  "- Business: $150"
        },
        "order": {
            "ua": "📦 Щоб замовити — напиши:\n👉 ХОЧУ БОТА",
            "en": "📦 To order — type:\n👉 I WANT BOT"
        },
        "contact": {
            "ua": "📞 Контакт: @Life_Industryl",
            "en": "📞 Contact: @Life_Industryl"
        }
    }

    return texts[key][lang]

# ======================
# 🚀 START
# ======================

@bot.message_handler(commands=['start'])
def start(message):
    add_user(message.from_user)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🇺🇦 Українська", "🇬🇧 English")

    bot.send_message(message.chat.id, get_text(message.chat.id, "start"), reply_markup=markup)

# ======================
# 🌍 LANGUAGE SELECT
# ======================

@bot.message_handler(func=lambda m: m.text in ["🇺🇦 Українська", "🇬🇧 English"])
def set_lang(message):
    if "Українська" in message.text:
        user_lang[message.chat.id] = "ua"
    else:
        user_lang[message.chat.id] = "en"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("🤖 Info", "💰 Price")
    markup.add("📦 Order", "📞 Contact")

    bot.send_message(message.chat.id, get_text(message.chat.id, "menu"), reply_markup=markup)

# ======================
# 🔐 ADMIN
# ======================

@bot.message_handler(commands=['admin'])
def admin(message):
    try:
        password = message.text.split()[1]

        if password == ADMIN_PASSWORD:
            admin_mode.add(message.chat.id)

            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            markup.add("📊 Stats", "📢 Broadcast")
            markup.add("📈 Leads", "🟢 ON/OFF")

            bot.send_message(message.chat.id, "🔐 ADMIN PANEL", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "❌ Wrong password")
    except:
        bot.send_message(message.chat.id, "Usage: /admin password")

# ======================
# 📢 BROADCAST
# ======================

def broadcast_start(message):
    waiting_broadcast.add(message.chat.id)
    bot.send_message(message.chat.id, "✉️ Send text")

# ======================
# 🤖 MAIN HANDLER
# ======================

@bot.message_handler(func=lambda m: True)
def handler(message):

    global bot_active

    if not bot_active:
        bot.send_message(message.chat.id, "⛔ Bot disabled")
        return

    add_lead(message.chat.id)

    if message.chat.id in waiting_broadcast:
        waiting_broadcast.remove(message.chat.id)

        for u in get_users():
            try:
                bot.send_message(u, message.text)
            except:
                pass

        bot.send_message(message.chat.id, "✅ Sent")
        return

    text = message.text

    if text == "🤖 Info":
        bot.send_message(message.chat.id, get_text(message.chat.id, "info"))

    elif text == "💰 Price":
        bot.send_message(message.chat.id, get_text(message.chat.id, "price"))

    elif text == "📦 Order":
        bot.send_message(message.chat.id, get_text(message.chat.id, "order"))

    elif text == "📞 Contact":
        bot.send_message(message.chat.id, get_text(message.chat.id, "contact"))

    elif message.chat.id in admin_mode:

        if text == "📊 Stats":
            bot.send_message(message.chat.id,
                f"Users: {count_users()}\nLeads: {count_leads()}")

        elif text == "📈 Leads":
            bot.send_message(message.chat.id,
                f"Leads: {count_leads()}")

        elif text == "📢 Broadcast":
            broadcast_start(message)

        elif text == "🟢 ON/OFF":
            bot_active = not bot_active
            bot.send_message(message.chat.id, f"Bot: {bot_active}")

# ======================
# 🚀 RUN
# ======================

print("🚀 Bot started...")
bot.infinity_polling()
