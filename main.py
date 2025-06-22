import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
import random
import os

TOKEN = "7567294339:AAG1dAC8bvS-caIHhIMLsnbKa1b3mCDiL2c"
bot = telebot.TeleBot(TOKEN)

users_file = "data.json"
if not os.path.exists(users_file):
    with open(users_file, "w") as f:
        json.dump({}, f)

def load_users():
    with open(users_file, "r") as f:
        return json.load(f)

def save_users(users):
    with open(users_file, "w") as f:
        json.dump(users, f)

def get_user(user_id):
    users = load_users()
    if str(user_id) not in users:
        users[str(user_id)] = {
            "level": 1,
            "exp": 0,
            "gold": 100,
            "hp": 100,
            "guild": None,
            "skills": {"strength": 0, "agility": 0, "defense": 0},
            "points": 0,
            "armor": "Нет"
        }
        save_users(users)
    return users[str(user_id)]

def update_user(user_id, data):
    users = load_users()
    users[str(user_id)].update(data)
    save_users(users)

def get_main_menu():
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("⚔️ Бой", callback_data="battle"),
        InlineKeyboardButton("📍 Острова", callback_data="islands")
    )
    markup.row(
        InlineKeyboardButton("📦 Клад", callback_data="treasure"),
        InlineKeyboardButton("🎒 Скиллы", callback_data="skills")
    )
    markup.row(
        InlineKeyboardButton("🛡 Гильдия", callback_data="guild"),
        InlineKeyboardButton("🏆 Рейтинг", callback_data="rating")
    )
    markup.row(
        InlineKeyboardButton("💬 Чат", callback_data="chat")
    )
    return markup

@bot.message_handler(commands=["start"])
def start(message):
    get_user(message.chat.id)
    bot.send_message(message.chat.id, "🏴‍☠️ Привет, пират! Добро пожаловать в игру!", reply_markup=get_main_menu())

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = str(call.message.chat.id)
    user = get_user(user_id)

    if call.data == "battle":
        damage = random.randint(5, 20)
        armor_bonus = {"Нет": 0, "Бронза": 2, "Сталь": 5, "Магия": 8}
        damage = max(0, damage - armor_bonus.get(user["armor"], 0))
        user["hp"] -= damage
        exp = random.randint(10, 25)
        user["exp"] += exp
        result = f"⚔️ Ты сразился и потерял {damage} HP. Получено опыта: {exp}."

        if user["exp"] >= user["level"] * 100:
            user["exp"] = 0
            user["level"] += 1
            user["points"] += 3
            user["gold"] += 50
            user["hp"] = 100
            result += f" ✨ Уровень повышен до {user['level']}! +3 очка навыков!"

        update_user(user_id, user)
        bot.edit_message_text(result, call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

    elif call.data == "islands":
        markup = InlineKeyboardMarkup()
        markup.row(
            InlineKeyboardButton("🏝 Черепов", callback_data="isle_skull"),
            InlineKeyboardButton("🌩 Шторма", callback_data="isle_storm")
        )
        markup.row(
            InlineKeyboardButton("💰 Золота", callback_data="isle_gold"),
            InlineKeyboardButton("🔮 Кристаллов", callback_data="isle_crystal")
        )
        markup.row(InlineKeyboardButton("🔙 Назад", callback_data="back"))
        bot.edit_message_text("Выбери остров:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("isle_"):
        bot.edit_message_text("Ты исследуешь остров... 🧭", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

    elif call.data == "treasure":
        found = random.choices(["gold", "nothing", "rare"], [0.6, 0.3, 0.1])[0]
        if found == "gold":
            amount = random.randint(20, 100)
            user["gold"] += amount
            msg = f"🪙 Ты нашел клад: {amount} золота!"
        elif found == "rare":
            user["armor"] = random.choice(["Бронза", "Сталь", "Магия"])
            msg = f"🧥 Ты нашел редкий доспех: {user['armor']}!"
        else:
            msg = "😕 Ничего не найдено."
        update_user(user_id, user)
        bot.edit_message_text(msg, call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

    elif call.data == "skills":
        markup = InlineKeyboardMarkup()
        for skill in ["strength", "agility", "defense"]:
            markup.row(InlineKeyboardButton(f"⬆️ {skill.capitalize()} ({user['skills'][skill]})", callback_data=f"skill_{skill}"))
        markup.row(InlineKeyboardButton("🔙 Назад", callback_data="back"))
        bot.edit_message_text(f"🎯 Очков навыков: {user['points']}", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("skill_"):
        skill = call.data.split("_")[1]
        if user["points"] > 0:
            user["skills"][skill] += 1
            user["points"] -= 1
            update_user(user_id, user)
            bot.answer_callback_query(call.id, f"{skill.capitalize()} прокачан!")
        else:
            bot.answer_callback_query(call.id, "Недостаточно очков.")
        callback(call)

    elif call.data == "guild":
        markup = InlineKeyboardMarkup()
        if user["guild"]:
            markup.row(InlineKeyboardButton(f"🚪 Покинуть гильдию ({user['guild']})", callback_data="leave_guild"))
        else:
            markup.row(
                InlineKeyboardButton("🌊 Кровавые волны", callback_data="join_wave"),
                InlineKeyboardButton("👻 Призрачные паруса", callback_data="join_ghost")
            )
            markup.row(InlineKeyboardButton("💀 Черепа бури", callback_data="join_skull"))
        markup.row(InlineKeyboardButton("🔙 Назад", callback_data="back"))
        bot.edit_message_text("Гильдия:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif call.data.startswith("join_"):
        guilds = {
            "wave": "🌊 Кровавые волны",
            "ghost": "👻 Призрачные паруса",
            "skull": "💀 Черепа бури"
        }
        chosen = call.data.split("_")[1]
        user["guild"] = guilds[chosen]
        update_user(user_id, user)
        bot.edit_message_text(f"✅ Ты вступил в гильдию: {user['guild']}", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

    elif call.data == "leave_guild":
        user["guild"] = None
        update_user(user_id, user)
        bot.edit_message_text("🚪 Ты покинул гильдию.", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

    elif call.data == "rating":
        users = load_users()
        top = sorted(users.items(), key=lambda x: x[1]["level"], reverse=True)[:5]
        text = """🏆 ТОП пиратов:"""

        for i, (uid, data) in enumerate(top, 1):
            guild = data["guild"] or "без гильдии"
            text += f"{i}. ID {uid} — Ур. {data['level']} ({guild})\n"
        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

    elif call.data == "chat":
        bot.send_message(call.message.chat.id, "✉️ Напиши сообщение для пиратского чата:")

    elif call.data == "back":
        bot.edit_message_text("🔙 Возврат в главное меню:", call.message.chat.id, call.message.message_id, reply_markup=get_main_menu())

@bot.message_handler(func=lambda m: True)
def handle_chat(m):
    if m.text and len(m.text) < 200:
        users = load_users()
        text = f"📣 [Пират {m.from_user.id}]: {m.text}"
        for uid in users:
            if uid != str(m.chat.id):
                try:
                    bot.send_message(uid, text)
                except:
                    continue
        bot.send_message(m.chat.id, "✅ Сообщение отправлено пиратам!")

bot.polling(non_stop=True)
