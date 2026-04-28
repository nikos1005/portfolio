#!/usr/bin/env python3
"""
Telegram Weather Bot — простой и рабочий
"""

import os
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Конфигурация (заполни в .env)
BOT_TOKEN = os.getenv('BOT_TOKEN', 'ТОКЕН_ИЗ_BOTFATHER')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY', 'КЛЮЧ_OPENWEATHERMAP')
BASE_URL = 'https://api.openweathermap.org/data/2.5/weather'

# --- Хендлеры ---

async def start(update: Update, context: CallbackContext):
    """Приветствие"""
    text = (
        "🌤 Привет! Я — Weather Bot.\n\n"
        "Отправь мне:\n"
        "• /weather <город> — узнай погоду\n"
        "• Просто название города — тоже работает\n\n"
        "Пример: /weather Москва"
    )
    await update.message.reply_text(text)

async def help_cmd(update: Update, context: CallbackContext):
    """Помощь"""
    await update.message.reply_text(
        "🌦 *Команды:*\n\n"
        "/start — начать\n"
        "/weather <город> — погода\n"
        "/help — эта справка\n\n"
        "Поддерживаются русские и английские названия городов.",
        parse_mode='Markdown'
    )

async def weather(update: Update, context: CallbackContext):
    """Запрос погоды"""
    # Получаем город
    if context.args:
        city = ' '.join(context.args)
    else:
        await update.message.reply_text("Укажи город: /weather <название>")
        return

    await get_weather_and_reply(update, city)

async def handle_text(update: Update, context: CallbackContext):
    """Обработка простого текста (город без команды)"""
    city = update.message.text.strip()
    await get_weather_and_reply(update, city)

async def get_weather_and_reply(update: Update, city: str):
    """Получает погоду и отправляет"""
    try:
        # Запрос к OpenWeatherMap
        params = {
            'q': city,
            'appid': WEATHER_API_KEY,
            'units': 'metric',  # Celsius
            'lang': 'ru'  # русский язык
        }
        resp = requests.get(BASE_URL, params=params, timeout=10)
        data = resp.json()

        if resp.status_code != 200:
            error_msg = data.get('message', 'Unknown error')
            await update.message.reply_text(f"❌ Ошибка: {error_msg}")
            return

        # Парсим данные
        name = data['name']
        country = data['sys']['country']
        temp = data['main']['temp']
        feels_like = data['main']['feels_like']
        humidity = data['main']['humidity']
        wind = data['wind']['speed']
        description = data['weather'][0]['description'].capitalize()
        icon = data['weather'][0]['icon']

        # Формируем ответ
        text = (
            f"🌍 *{name}, {country}*\n\n"
            f"🌡 *Температура:* {temp}°C (ощущается как {feels_like}°C)\n"
            f"💧 *Влажность:* {humidity}%\n"
            f"💨 *Ветер:* {wind} м/с\n"
            f"☁️ *Состояние:* {description}\n\n"
            f"`Powered by OpenWeatherMap`"
        )

        # Отправляем погоду (можно добавить иконку)
        await update.message.reply_text(text, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

# --- Главная ---

def main():
    """Запуск бота"""
    if BOT_TOKEN == 'ТОКЕН_ИЗ_BOTFATHER':
        print("❌ Укажи BOT_TOKEN в .env или в коде!")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    # Регистрируем хендлеры
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help_cmd))
    app.add_handler(CommandHandler('weather', weather))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("🤖 Бот запущен...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
