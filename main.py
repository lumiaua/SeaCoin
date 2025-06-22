import os
import psycopg2
import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

DATABASE_URL = os.getenv("DATABASE_URL")
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

cursor.execute(
    '''
    CREATE TABLE IF NOT EXISTS users (
        user_id BIGINT PRIMARY KEY,
        seacoin INTEGER DEFAULT 0
    )
    '''
)
conn.commit()

bot = telebot.TeleBot(BOT_TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    cursor.execute("INSERT INTO users (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (user_id,))
    conn.commit()

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("⚓ Фармить SeaCoin"))
    bot.send_message(message.chat.id, "🏴‍☠️ Добро пожаловать, капитан! Нажми кнопку, чтобы фармить SeaCoin.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "⚓ Фармить SeaCoin")
def farm(message):
    user_id = message.from_user.id
    cursor.execute("UPDATE users SET seacoin = seacoin + 1 WHERE user_id = %s", (user_id,))
    conn.commit()
    cursor.execute("SELECT seacoin FROM users WHERE user_id = %s", (user_id,))
    coins = cursor.fetchone()[0]
    bot.send_message(message.chat.id, f"💰 Ты добыл 1 SeaCoin! Всего у тебя: {coins} монет.")

bot.polling()
