import os
import json
import random
from telebot import TeleBot, types
from datetime import datetime, timedelta

TOKEN = os.getenv("TOKEN")
bot = TeleBot(TOKEN)

START_DATE = datetime(2025, 2, 15)

PARTNERS = {
    896537397: 599175384,
    599175384: 896537397,
   
    
    }

user_states = {}
last_bonus = {}
bonus_streak = {}
achievements = {uid: set() for uid in PARTNERS}

# Кнопки
BAL_BTN = "💰 Баланс"
SEND_BTN = "💸 Надіслати цьомкогривні"
BONUS_BTN = "🎁 Щоденний цьомкобонус"
LOVE_BTN = "❤️ Дні разом"
ACHIEVE_BTN = "🏆 Досягнення"
BACK_BTN = "🔙 Назад"
CUSTOM_BTN = "💬 Свій варіант"
SHOP_BTN = "🍭 Магазин"
MOOD_BTN = "🧠 Настрій партнера"
RATE_DAY_BTN = "🌞 Оцінка дня"



# Магазин
SHOP_ITEMS = [
    {"emoji": "🏱", "name": "Сюрприз-день", "price": 15, "description": "\"Сьогодні твій день! Зроби зі мною, що хочеш 😘\""},
    {"emoji": "🎟️", "name": "Квиток на побачення", "price": 20, "description": "Пропозиція організувати побачення (бот нагадує)"},
    {"emoji": "💋", "name": "Купон на 10 цьомків", "price": 10, "description": "Зобов'язання партнера подарувати 10 поцілунків"},
    {"emoji": "☕", "name": "Ранкова кава", "price": 8, "description": "\"Твій партнер замовив тобі каву ☕\""},
    {"emoji": "🛎️", "name": "Ніч обійм", "price": 25, "description": "\"Сьогодні ввечері – обійми без обмежень 🛎️💖\""},
    {"emoji": "🐾", "name": "Подарунок-сюрприз", "price": 50, "description": "Випадковий з доступних товарів, можливо, рідкісний"}
]

# Меню

def main_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(BAL_BTN, SEND_BTN)
    kb.add(BONUS_BTN, LOVE_BTN)
    kb.add(ACHIEVE_BTN, SHOP_BTN)
    kb.add("18+")
    kb.add(RATE_DAY_BTN)
    kb.add(MOOD_BTN)
    return kb

def amount_keyboard():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("1", "3", "5", "10")
    kb.add(CUSTOM_BTN, BACK_BTN)
    return kb


# Старт
@bot.message_handler(commands=["start"])
def start(msg):
    uid = msg.from_user.id
    if uid not in PARTNERS:
        bot.send_message(uid, "❌ Ви не зареєстровані у Цьомкобанку.")
        return
    bot.send_message(uid, "👋 Вітаємо у Цьомкобанку!", reply_markup=main_keyboard())

# Баланс
@bot.message_handler(func=lambda m: m.text == BAL_BTN)
def check_balance(msg):
    uid = msg.from_user.id
    bal = BALANCES[uid]
    if bal > 200:
        achievements[uid].add("🏦 Багатій — Баланс перевищив 200 цьомкогривень")
    bot.send_message(uid, f"💼 Ваш баланс: {bal} цьомкогривень")
    save_data()

# Надіслати
@bot.message_handler(func=lambda m: m.text == SEND_BTN)
def choose_amount(msg):
    uid = msg.from_user.id
    if uid not in PARTNERS:
        return
    bot.send_message(uid, "Скільки цьомкогривень надіслати?", reply_markup=amount_keyboard())
    user_states[uid] = "choosing_amount"

@bot.message_handler(func=lambda m: m.text == MOOD_BTN)
def ask_partner_mood(msg):
    uid = msg.from_user.id
    partner = PARTNERS.get(uid)
    if not partner:
        return

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🟢", callback_data=f"mood_tender_{uid}"),
        types.InlineKeyboardButton("🟡", callback_data=f"mood_neutral_{uid}"),
        types.InlineKeyboardButton("🔴", callback_data=f"mood_angry_{uid}")
    )

    bot.send_message(partner, f"🔔 ар ю хорні?", reply_markup=kb)
    bot.send_message(uid, "⏳ Запит надіслано партнеру.")


# Назад
@bot.message_handler(func=lambda m: m.text == BACK_BTN)
def back_to_main(msg):
    user_states.pop(msg.from_user.id, None)
    bot.send_message(msg.chat.id, "⬅️ Назад у меню.", reply_markup=main_keyboard())

# Своя сума
@bot.message_handler(func=lambda m: m.text == CUSTOM_BTN)
def ask_custom_amount(msg):
    uid = msg.from_user.id
    bot.send_message(uid, "Введіть суму цьомкогривень:")
    user_states[uid] = "custom_amount"

# Обробка введеної суми
@bot.message_handler(func=lambda m: m.text.isdigit())
def handle_amount_input(msg):
    uid = msg.from_user.id
    state = user_states.get(uid)
    if state not in ["choosing_amount", "custom_amount"]:
        return

    amount = int(msg.text)
    if amount <= 0:
        bot.send_message(uid, "❌ Введіть позитивне число.")
        return
    if BALANCES[uid] < amount:
        bot.send_message(uid, "❌ Недостатньо цьомкогривень.")
        user_states.pop(uid, None)
        return

    partner = PARTNERS[uid]
    BALANCES[uid] -= amount
    BALANCES[partner] += amount

    if "🏑 Перший переказ — Здійснено перший переказ цьомкогривень" not in achievements[uid]:
        achievements[uid].add("🏑 Перший переказ — Здійснено перший переказ цьомкогривень")

    bot.send_message(uid, f"✅ Надіслано {amount} цьомкогривень!")
    bot.send_message(partner, f"💖 Вам надійшло {amount} цьомкогривень від {msg.from_user.first_name}!")

    user_states.pop(uid, None)
    bot.send_message(uid, "Що далі?", reply_markup=main_keyboard())
    save_data()

# Бонус
@bot.message_handler(func=lambda m: m.text == BONUS_BTN)
def daily_bonus(msg):
    uid = msg.from_user.id
    today = datetime.now().date()
    last = last_bonus.get(uid)

    if last == today:
        bot.send_message(uid, "🎁 Ви вже отримали сьогоднішній цьомкобонус.")
        return

    BALANCES[uid] += 10
    last_bonus[uid] = today
    bonus_streak[uid] = bonus_streak.get(uid, 0) + 1
    if bonus_streak[uid] >= 5:
        achievements[uid].add("🎁 Бонусник — Отримано 5 бонусів підряд")

    bot.send_message(uid, "🎉 Ви отримали 10 цьомкогривень!")
    save_data()

# День стосунків
@bot.message_handler(func=lambda m: m.text == LOVE_BTN)
def love_days(msg):
    uid = msg.from_user.id
    days = (datetime.now().date() - START_DATE.date()).days
    partner = PARTNERS[uid]

    if days >= 90:
        achievements[uid].add("💗 90 днів разом")
    if days >= 180:
        achievements[uid].add("💝 180 днів разом")

    bot.send_message(uid, f"💑 Ви разом вже {days} днів!")
    save_data()

# Досягнення
@bot.message_handler(func=lambda m: m.text == ACHIEVE_BTN)
def show_achievements(msg):
    uid = msg.from_user.id
    if not achievements[uid]:
        bot.send_message(uid, "😔 Поки що немає досягнень.")
    else:
        text = "🏆 Ваші досягнення:\n\n" + "\n".join(achievements[uid])
        bot.send_message(uid, text)

# Магазин
@bot.message_handler(func=lambda m: m.text == SHOP_BTN)
def open_shop(msg):
    uid = msg.from_user.id
    text = "🏨 *Магазин Цьомкобанку*\nОберіть товар для покупки:"
    kb = types.InlineKeyboardMarkup()
    for i, item in enumerate(SHOP_ITEMS):
        kb.add(types.InlineKeyboardButton(f"{item['emoji']} {item['name']} ({item['price']} цг)", callback_data=f"buy_{i}"))
    bot.send_message(uid, text, reply_markup=kb, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda c: c.data.startswith("buy_"))
def handle_purchase(call):
    uid = call.from_user.id
    item_index = int(call.data.split("_")[1])
    item = SHOP_ITEMS[item_index]

    if BALANCES[uid] < item['price']:
        bot.answer_callback_query(call.id, "❌ Недостатньо цьомкогривень")
        return

    BALANCES[uid] -= item['price']
    partner = PARTNERS[uid]

    if item['name'] == "Подарунок-сюрприз":
        surprise = random.choice(SHOP_ITEMS[:-1])
        bot.send_message(partner, f"🎁 Вам надійшов сюрприз: {surprise['emoji']} {surprise['name']}!\n{surprise['description']}")
    else:
        bot.send_message(partner, f"🎁 Ваш партнер купив для вас: {item['emoji']} {item['name']}\n{item['description']}")

    bot.answer_callback_query(call.id, f"✅ Куплено: {item['name']}")
    bot.send_message(uid, f"✔️ Ви купили {item['emoji']} {item['name']} за {item['price']} цьомкогривень")
    save_data()

# Інше
    # Реакція на конкретний символ
@bot.message_handler(func=lambda m: m.text == "⬅")
def handle_star(msg):
    bot.send_message(msg.chat.id, "Моя кохана, з Днем народження тебе! Сьогодні — особливий день. День, коли світ став кращим, бо в ньому з'явилася ти. Я не можу передати словами, наскільки щасливий, що саме тебе подарувало мені життя. Ти — моє сонце, моє натхнення, моя підтримка, моя ніжність і моє серце. З кожним днем я лише сильніше переконуюсь у тому, що ти — саме та, кого я так довго шукав. Я дякую тобі за кожну мить, за кожну усмішку, за кожне «люблю», яке ти даруєш. Бажаю тобі тепла, радості, спокою, здоров’я і натхнення. Але найбільше — щоб ти завжди відчувала себе коханою. Я зроблю усе можливе, щоб так і було. Ти заслуговуєш на все найкраще в цьому світі. Нехай цей день буде яскравим і щасливим, а поруч із тобою завжди буде той, хто любитиме тебе всім серцем. І я хочу бути саме тим. Зі святом, моя любов.")

@bot.message_handler(func=lambda m: m.text == "18+")
def request_options(msg):
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("Активний", callback_data="request_hug"),
        types.InlineKeyboardButton("Пасивний", callback_data="request_tea")
    )
    bot.send_message(msg.chat.id, "Який секс ти хочеш ?", reply_markup=kb)
@bot.message_handler(func=lambda m: m.text == RATE_DAY_BTN)
def rate_day(msg):
    uid = msg.from_user.id
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add("😊 Хороший", "🙂 Нормальний")
    kb.add("😐 Поганий", "☹️ Дуже поганий")
    kb.add("😖 Жахливий", BACK_BTN)
    bot.send_message(uid, "Як пройшов твій день? Обери варіант:", reply_markup=kb)
    user_states[uid] = "rating_day"

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "rating_day")
def handle_day_rating(msg):
    uid = msg.from_user.id
    partner = PARTNERS.get(uid)
    choice = msg.text

    if choice not in ["😊 Хороший", "🙂 Нормальний", "😐 Поганий", "☹️ Дуже поганий", "😖 Жахливий"]:
        bot.send_message(uid, "Будь ласка, обери один із варіантів 😉")
        return

    # Повідомлення партнеру
    bot.send_message(partner, f"💌 Твій партнер оцінив свій день як: {choice}")
    bot.send_message(uid, "Дякую за відповідь 💖", reply_markup=main_keyboard())
    user_states.pop(uid, None)

    
@bot.message_handler(func=lambda m: True)
def fallback(msg):
    bot.send_message(msg.chat.id, "😅 Не зовсім зрозумів. Оберіть дію з меню.", reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda c: c.data.startswith("request_"))
def send_request_to_partner(call):
    uid = call.from_user.id
    partner = PARTNERS[uid]
    what = call.data.replace("request_", "")
    text_map = {
        "hug": "активний",
        "tea": "пасивний"
    }
    text = text_map.get(what, "Щось гарне")

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Підтвердити", callback_data=f"confirm_{what}_{uid}"),
        types.InlineKeyboardButton("❌ Відхилити", callback_data=f"reject_{what}_{uid}")
    )

    bot.send_message(partner, f"Вам надійшов запит на *{text}* секс", parse_mode="Markdown", reply_markup=kb)
    bot.answer_callback_query(call.id, f"Запит «{text}» надіслано!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("confirm_"))
def confirm_request(call):
    parts = call.data.split("_")
    what = parts[1]
    sender_id = int(parts[2])
    text_map = {
        "hug": "активний секс",
        "tea": "пасивний секс"
    }
    text = text_map.get(what, "щось приємне")
    bot.send_message(sender_id, f"✅ Партнер погодився на {text}")
    bot.answer_callback_query(call.id, "Підтверджено!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("reject_"))
def reject_request(call):
    parts = call.data.split("_")
    what = parts[1]
    sender_id = int(parts[2])
    text_map = {
        "hug": "активний секс",
        "tea": "пасивний секс"
    }
    text = text_map.get(what, "ваш запит")
    bot.send_message(sender_id, f"❌ Партнер відхилив запит на {text}.")
    bot.answer_callback_query(call.id, "Відхилено!")

@bot.callback_query_handler(func=lambda c: c.data.startswith("mood_"))
def handle_mood_response(call):
    parts = call.data.split("_")
    mood = parts[1]
    requester_id = int(parts[2])
    mood_map = {
        "tender": "🟢",
        "neutral": "🟡",
        "angry": "🔴"
    }
    mood_text = mood_map.get(mood, "невідомий")

    bot.send_message(requester_id, f"📊 Хорнi партнера: *{mood_text}*", parse_mode="Markdown")
    bot.answer_callback_query(call.id, "✅ Відповідь надіслана!")

# Збереження/Завантаження
DATA_FILE = "data.json"

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "balances": BALANCES,
            "last_bonus": {str(k): v.isoformat() for k, v in last_bonus.items()},
            "bonus_streak": bonus_streak,
            "achievements": {str(k): list(v) for k, v in achievements.items()}
        }, f, ensure_ascii=False, indent=2)

def load_data():
    global BALANCES, last_bonus, bonus_streak, achievements
    if not os.path.exists(DATA_FILE):
        return
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        raw = json.load(f)
        BALANCES = {int(k): v for k, v in raw["balances"].items()}
        last_bonus = {int(k): datetime.fromisoformat(v).date() for k, v in raw["last_bonus"].items()}
        bonus_streak = {int(k): v for k, v in raw["bonus_streak"].items()}
        achievements = {int(k): set(v) for k, v in raw["achievements"].items()}

load_data()
bot.infinity_polling()


