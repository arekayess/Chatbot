import os
import logging
from flask import Flask
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler
import nest_asyncio
import asyncio

# Настройки логгера
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask-приложение
app = Flask(__name__)

@app.route('/')
def index():
    return '🤖 Бот работает!'

# Телеграм бот: приветствие
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Финансовые вопросы", callback_data="finance")],
        [InlineKeyboardButton("Личный кабинет", callback_data="account")]
    ]
    await update.message.reply_text(
        "Привет, на связи ассистент Финуслуг! Задайте вопрос или используйте кнопки, чтобы узнать больше 🔎",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# Обработка кнопок
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "finance":
        keyboard = [
            [InlineKeyboardButton("Вклады", callback_data="deposit")],
            [InlineKeyboardButton("ОСАГО", callback_data="osago")],
            [InlineKeyboardButton("Кредиты", callback_data="credit")],
            [InlineKeyboardButton("🔙 Вернуться назад", callback_data="back_main")]
        ]
        await query.edit_message_text("Выберите интересующий вас вопрос:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif data == "account":
        await query.edit_message_text("Если у Вас возникли вопросы по поводу вашего личного кабинета…")

    elif data == "deposit":
        await query.edit_message_text("У нас есть 824 предложений от надежных банков…")

    elif data == "osago":
        await query.edit_message_text("Полис ОСАГО за 5 минут…")

    elif data == "credit":
        await query.edit_message_text("Заполните анкету и мы подберем кредиты…")

    elif data == "back_main":
        keyboard = [
            [InlineKeyboardButton("Финансовые вопросы", callback_data="finance")],
            [InlineKeyboardButton("Личный кабинет", callback_data="account")]
        ]
        await query.edit_message_text("Привет, на связи ассистент Финуслуг! Задайте вопрос или используйте кнопки, чтобы узнать больше 🔎",
                                      reply_markup=InlineKeyboardMarkup(keyboard))

# Инициализация телеграм-бота
async def start_bot():
    token = os.getenv("BOT_TOKEN")  # Обязательно установи переменную окружения в Render

    if not token:
        logger.error("Переменная окружения BOT_TOKEN не установлена!")
        return

    app_telegram = ApplicationBuilder().token(token).build()
    app_telegram.add_handler(CommandHandler("start", start))
    app_telegram.add_handler(CallbackQueryHandler(button_handler))

    logger.info("🤖 Бот запущен...")
    await app_telegram.initialize()
    await app_telegram.start()
    await app_telegram.updater.start_polling()

# Запуск Flask и Telegram
if __name__ == "__main__":
    nest_asyncio.apply()  # Исправляем конфликт asyncio в Flask + PTB

    loop = asyncio.get_event_loop()
    loop.create_task(start_bot())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)