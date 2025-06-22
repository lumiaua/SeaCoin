import os
import psycopg2
from telebot import TeleBot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = os.getenv("7567294339:AAG1dAC8bvS-caIHhIMLsnbKa1b3mCDiL2c")
bot = TeleBot(TOKEN)

DATABASE_URL = os.getenv("DATABASE_URL")
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    seacoin INTEGER DEFAULT 0
)
''')
conn.commit()

def add_user(user_id):
    cursor.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
    conn.commit()

def get_user_seacoin(user_id):
    cursor.execute("SELECT seacoin FROM users WHERE user_id = %s", (user_id,))
    row = cursor.fetchone()
    return row[0] if row else 0

def update_seacoin(user_id, amount):
    cursor.execute("UPDATE users SET seacoin = seacoin + %s WHERE user_id = %s", (amount, user_id))
    conn.commit()

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    add_user(user_id)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⚓ Фармить SeaCoin"))

    bot.send_message(message.chat.id, "🏴‍☠️ Добро пожаловать, капитан!", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text == "⚓ Фармить SeaCoin")
def handle_farm(message):
    user_id = message.from_user.id
    update_seacoin(user_id, 1)
    coins = get_user_seacoin(user_id)
    bot.send_message(message.chat.id, f"💰 Ты добыл 1 SeaCoin! Всего у тебя: {coins}")

bot.polling()
