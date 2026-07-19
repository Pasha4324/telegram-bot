import telebot
from telebot import types
import sqlite3
import threading
from flask import Flask
from datetime import datetime


# ======================
# WEB FOR RENDER
# ======================

app = Flask(__name__)


@app.route("/")
def home():
    return "Bot is running 🚀"


def run_web():
    app.run(
        host="0.0.0.0",
        port=10000
    )


# ======================
# TOKEN
# ======================

TOKEN = "8783803376:AAEur4LCzVKNamZYXjn16oc_ZLBqiEijryA"

bot = telebot.TeleBot(TOKEN)


# ======================
# CONFIG
# ======================

ADMIN_PASSWORD = "856243"

user_lang = {}
bot_active = True


# ======================
# DATABASE
# ======================

conn = sqlite3.connect(
    "sales.db",
    check_same_thread=False
)

cur = conn.cursor()


# USERS

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
username TEXT,
balance REAL DEFAULT 0,
created TEXT
)
""")


# LEADS

cur.execute("""
CREATE TABLE IF NOT EXISTS leads(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
created TEXT
)
""")


# CATEGORIES

cur.execute("""
CREATE TABLE IF NOT EXISTS categories(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT
)
""")


# PRODUCTS

cur.execute("""
CREATE TABLE IF NOT EXISTS products(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
category TEXT,
description TEXT,
price REAL,
photo TEXT,
featured INTEGER DEFAULT 0,
discount INTEGER DEFAULT 0
)
""")


# ORDERS

cur.execute("""
CREATE TABLE IF NOT EXISTS orders(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
product_id INTEGER,
status TEXT,
amount REAL,
created TEXT
)
""")


# PAYMENTS

cur.execute("""
CREATE TABLE IF NOT EXISTS payments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
order_id INTEGER,
method TEXT,
status TEXT,
created TEXT
)
""")


# LICENSES

cur.execute("""
CREATE TABLE IF NOT EXISTS licenses(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
product_id INTEGER,
license_key TEXT
)
""")


# PROMO

cur.execute("""
CREATE TABLE IF NOT EXISTS promo_codes(
id INTEGER PRIMARY KEY AUTOINCREMENT,
code TEXT,
discount INTEGER
)
""")


# REVIEWS

cur.execute("""
CREATE TABLE IF NOT EXISTS reviews(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
product_id INTEGER,
stars INTEGER,
text TEXT
)
""")


# FAVORITES

cur.execute("""
CREATE TABLE IF NOT EXISTS favorites(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
product_id INTEGER
)
""")


# REFERRALS

cur.execute("""
CREATE TABLE IF NOT EXISTS referrals(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
ref_user INTEGER,
profit REAL DEFAULT 0
)
""")


# ADMINS

cur.execute("""
CREATE TABLE IF NOT EXISTS admins(
id INTEGER PRIMARY KEY,
username TEXT,
role TEXT DEFAULT 'admin'
)
""")


# LOGS

cur.execute("""
CREATE TABLE IF NOT EXISTS logs(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
action TEXT,
created TEXT
)
""")


conn.commit()


# ======================
# DATABASE FUNCTIONS
# ======================


def add_user(user):

    cur.execute(
        """
        INSERT OR IGNORE INTO users
        (id, username, created)
        VALUES (?,?,?)
        """,
        (
            user.id,
            user.username,
            str(datetime.now())
        )
    )

    conn.commit()



def add_lead(uid):

    cur.execute(
        """
        INSERT INTO leads
        (user_id, created)
        VALUES (?,?)
        """,
        (
            uid,
            str(datetime.now())
        )
    )

    conn.commit()



def add_log(uid, action):

    cur.execute(
        """
        INSERT INTO logs
        (user_id, action, created)
        VALUES (?,?,?)
        """,
        (
            uid,
            action,
            str(datetime.now())
        )
    )

    conn.commit()



def is_admin(uid):

    cur.execute(
        """
        SELECT id FROM admins
        WHERE id=?
        """,
        (uid,)
    )

    return cur.fetchone() is not None



def add_admin(user):

    cur.execute(
        """
        INSERT OR IGNORE INTO admins
        (id,username)
        VALUES (?,?)
        """,
        (
            user.id,
            user.username
        )
    )

    conn.commit()



def stats():

    cur.execute(
        "SELECT COUNT(*) FROM users"
    )

    users = cur.fetchone()[0]


    cur.execute(
        "SELECT COUNT(*) FROM orders"
    )

    orders = cur.fetchone()[0]


    cur.execute(
        "SELECT COUNT(*) FROM products"
    )

    products = cur.fetchone()[0]


    return users, orders, products



# ======================
# DEFAULT CATEGORIES
# ======================

def create_categories():

    categories = [
        "🤖 Telegram Bots",
        "🌐 Websites",
        "💻 Source Code",
        "🖥 VPS / Servers",
        "⚙ APIs",
        "📦 Custom Development"
    ]


    for c in categories:

        cur.execute(
            """
            INSERT OR IGNORE INTO categories(name)
            VALUES(?)
            """,
            (c,)
        )


    conn.commit()



create_categories()

# ======================
# TEXT SYSTEM
# ======================


def text(uid, key):

    lang = user_lang.get(uid, "ua")


    data = {

        "start": {
            "ua": "👋 Вітаю!\nОберіть мову:",
            "en": "👋 Welcome!\nChoose language:"
        },


        "menu": {
            "ua": "👇 Головне меню:",
            "en": "👇 Main menu:"
        },


        "support": {
            "ua": "📞 Підтримка:\n@Life_Industryl",
            "en": "📞 Support:\n@Life_Industryl"
        },


        "profile": {
            "ua": "👤 Ваш профіль",
            "en": "👤 Your profile"
        }

    }


    return data[key][lang]



# ======================
# KEYBOARDS
# ======================


def main_menu():

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )


    kb.add(
        "🏠 Home",
        "🛍 Shop"
    )

    kb.add(
        "📂 Categories",
        "⭐ Popular"
    )

    kb.add(
        "🔥 Discounts",
        "👤 Profile"
    )

    kb.add(
        "📞 Support"
    )


    return kb



def categories_menu():


    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )


    cur.execute(
        "SELECT name FROM categories"
    )


    cats = cur.fetchall()


    for c in cats:

        kb.add(c[0])


    kb.add("⬅ Back")


    return kb



# ======================
# START
# ======================


@bot.message_handler(commands=["start"])
def start(message):

    add_user(
        message.from_user
    )


    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )


    kb.add(
        "🇺🇦 Українська",
        "🇬🇧 English"
    )


    bot.send_message(
        message.chat.id,
        text(
            message.chat.id,
            "start"
        ),
        reply_markup=kb
    )



# ======================
# LANGUAGE
# ======================


@bot.message_handler(
    func=lambda m:
    m.text in [
        "🇺🇦 Українська",
        "🇬🇧 English"
    ]
)

def language(message):


    if "Українська" in message.text:

        user_lang[
            message.chat.id
        ] = "ua"


    else:

        user_lang[
            message.chat.id
        ] = "en"



    bot.send_message(
        message.chat.id,
        text(
            message.chat.id,
            "menu"
        ),
        reply_markup=main_menu()
    )



# ======================
# SHOP
# ======================


def show_products(uid):


    cur.execute(
        """
        SELECT id,name,description,price
        FROM products
        """
    )


    products = cur.fetchall()


    if not products:


        bot.send_message(
            uid,
            "🛒 Поки товарів немає"
        )

        return



    for p in products:


        kb = types.InlineKeyboardMarkup()


        kb.add(
            types.InlineKeyboardButton(
                "🛒 Buy",
                callback_data=f"buy_{p[0]}"
            )
        )


        bot.send_message(
            uid,
            f"""
🛍 {p[1]}

{p[2]}

💵 Price:
${p[3]}
""",
            reply_markup=kb
        )



# ======================
# PROFILE
# ======================


def profile(uid):


    cur.execute(
        """
        SELECT username,balance
        FROM users
        WHERE id=?
        """,
        (uid,)
    )


    user = cur.fetchone()


    if user:


        bot.send_message(
            uid,
            f"""
👤 Profile

Username:
@{user[0]}

Balance:
${user[1]}

📦 Purchases
⭐ Favorites
🎁 Referral
"""
        )



# ======================
# ORDERS
# ======================


def create_order(uid, product_id):


    cur.execute(
        """
        SELECT price
        FROM products
        WHERE id=?
        """,
        (product_id,)
    )


    product = cur.fetchone()


    if not product:
        return



    cur.execute(
        """
        INSERT INTO orders
        (user_id,product_id,status,amount,created)
        VALUES (?,?,?,?,?)
        """,
        (
            uid,
            product_id,
            "Waiting payment",
            product[0],
            str(datetime.now())
        )
    )


    conn.commit()


    order_id = cur.lastrowid



    bot.send_message(
        uid,
        f"""
📦 Order №{order_id}

Amount:
${product[0]}

Status:
Waiting for payment...

💳 Choose payment:
"""
    )



# ======================
# CALLBACKS
# ======================


@bot.callback_query_handler(
    func=lambda call: True
)

def callbacks(call):


    if call.data.startswith("buy_"):


        product_id = int(
            call.data.split("_")[1]
        )


        create_order(
            call.message.chat.id,
            product_id
        )
        # ======================
# ADMIN PANEL
# ======================


def admin_menu(uid):

    kb = types.ReplyKeyboardMarkup(
        resize_keyboard=True
    )


    kb.add(
        "📊 Statistics",
        "🛍 Products"
    )

    kb.add(
        "📂 Categories",
        "📦 Orders"
    )

    kb.add(
        "💳 Payments",
        "👥 Users"
    )

    kb.add(
        "🎁 Promo Codes",
        "⭐ Reviews"
    )

    kb.add(
        "📢 Broadcast",
        "⚙ Settings"
    )

    bot.send_message(
        uid,
        "🔐 ADMIN PANEL",
        reply_markup=kb
    )



@bot.message_handler(commands=["admin"])
def admin(message):

    try:

        password = message.text.split()[1]


        if password == ADMIN_PASSWORD:


            add_admin(
                message.from_user
            )


            add_log(
                message.chat.id,
                "Admin login"
            )


            bot.send_message(
                message.chat.id,
                "✅ Admin activated"
            )


            admin_menu(
                message.chat.id
            )


        else:


            bot.send_message(
                message.chat.id,
                "❌ Wrong password"
            )


    except:


        bot.send_message(
            message.chat.id,
            "/admin password"
        )



# ======================
# ADMIN PRODUCTS
# ======================


def admin_products(uid):


    cur.execute(
        """
        SELECT id,name,price
        FROM products
        """
    )


    products = cur.fetchall()


    if not products:


        bot.send_message(
            uid,
            "🛍 Products empty"
        )

        return



    text = "🛍 PRODUCTS\n\n"


    for p in products:


        text += (
            f"#{p[0]} "
            f"{p[1]} "
            f"${p[2]}\n"
        )


    bot.send_message(
        uid,
        text
    )



# ======================
# MAIN HANDLER
# ======================


@bot.message_handler(
    func=lambda m: True
)

def handler(message):


    global bot_active


    if not bot_active:

        return



    uid = message.chat.id

    t = message.text


    add_user(
        message.from_user
    )


    add_lead(uid)



    # ADMIN


    if is_admin(uid):


        if t == "📊 Statistics":


            u,o,p = stats()


            bot.send_message(
                uid,
                f"""
📊 Statistics

👥 Users:
{u}

📦 Orders:
{o}

🛍 Products:
{p}
"""
            )

            return



        elif t == "🛍 Products":


            admin_products(uid)

            return



        elif t == "⚙ Settings":


            bot.send_message(
                uid,
                "⚙ Settings"
            )

            return



    # USER MENU


    if t == "🏠 Home":


        bot.send_message(
            uid,
            text(uid,"menu"),
            reply_markup=main_menu()
        )



    elif t == "🛍 Shop":


        show_products(uid)



    elif t == "📂 Categories":


        bot.send_message(
            uid,
            "📂 Categories",
            reply_markup=categories_menu()
        )



    elif t == "👤 Profile":


        profile(uid)



    elif t == "📞 Support":


        bot.send_message(
            uid,
            text(uid,"support")
        )



    elif t == "⬅ Back":


        bot.send_message(
            uid,
            text(uid,"menu"),
            reply_markup=main_menu()
        )



# ======================
# RUN
# ======================


if __name__ == "__main__":


    threading.Thread(
        target=run_web
    ).start()



    print(
        "🚀 Bot started..."
    )


    bot.infinity_polling()
