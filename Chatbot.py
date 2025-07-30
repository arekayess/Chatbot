import logging
import asyncio
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.error import BadRequest

BOT_TOKEN = "8188612626:AAFplAo1fUxgdcB3wu5pEfPVot3fwgWCTWY"
ADMIN_CHAT_ID = 7742758052

# --- Тексты и меню ---
WELCOME_TEXT = "Привет, на связи ассистент Финуслуг!\nЗадайте вопрос или используйте кнопки, чтобы узнать больше 🔎"
CABINET_TEXT = "Если у Вас возникли вопросы по поводу вашего личного кабинета,\nВы можете обратиться по номеру технического отдела: +7 (999) 123-45-67"
VKLADY_TEXT = "У нас есть 824 предложений от надежных банков... доходность до 30%."
OSAGO_TEXT = "Полис ОСАГО за 5 минут... от 21 страховой компании."
CREDIT_TEXT = "Заполните анкету и мы подберем кредиты..."

def main_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💰 Финансовые вопросы", callback_data="finance")],
        [InlineKeyboardButton("👤 Личный кабинет", callback_data="cabinet")],
    ])

def finance_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🪙 Вклады", callback_data="vklady")],
        [InlineKeyboardButton("🚗 ОСАГО", callback_data="osago")],
        [InlineKeyboardButton("💳 Кредиты", callback_data="credit")],
        [InlineKeyboardButton("🔙 Вернуться назад", callback_data="back")],
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(WELCOME_TEXT, reply_markup=main_menu())
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"📥 Новый пользователь: @{user.username or user.first_name} ({user.id})"
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user = query.from_user
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"👆 @{user.username or user.first_name} нажал кнопку: {data}"
    )

    try:
        if data == "finance":
            await query.edit_message_text("Выберите категорию:", reply_markup=finance_menu())
        elif data == "cabinet":
            await query.edit_message_text(CABINET_TEXT, reply_markup=main_menu())
        elif data == "vklady":
            await query.edit_message_text(VKLADY_TEXT, reply_markup=finance_menu())
        elif data == "osago":
            await query.edit_message_text(OSAGO_TEXT, reply_markup=finance_menu())
        elif data == "credit":
            await query.edit_message_text(CREDIT_TEXT, reply_markup=finance_menu())
        elif data == "back":
            await query.edit_message_text("Выберите действие:", reply_markup=main_menu())
    except BadRequest as e:
        if "Message is not modified" not in str(e):
            raise

async def admin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.id != ADMIN_CHAT_ID:
        await update.message.reply_text("⛔ У вас нет доступа.")
        return
    try:
        target_id = int(context.args[0])
        text_to_send = ' '.join(context.args[1:])
        await context.bot.send_message(chat_id=target_id, text=text_to_send)
        await update.message.reply_text("✅ Сообщение отправлено.")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def run_bot():
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(CommandHandler("msg", admin_message))

    print("🤖 Бот запущен...")
    await app.run_polling()

# --- Flask-заглушка для Render ---
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "Бот работает!"

def run_flask():
    flask_app.run(host="0.0.0.0", port=10000)

if __name__ == '__main__':
    threading.Thread(target=run_flask).start()  # Flask заглушка
    asyncio.run(run_bot())   