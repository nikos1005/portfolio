# 🤖 Telegram Weather Bot

Бот, который присылает погоду по городу.

## Возможности:
- `/start` — приветствие
- `/weather <город>` — погода в городе
- Автоопределение города (если не указан)
- Поддержка русских и английских названий

## Технологии:
- Python 3.8+
- python-telegram-bot
- OpenWeatherMap API (бесплатно 1000 запросов/день)

## Установка:

```bash
# 1. Установи зависимости
pip install python-telegram-bot requests

# 2. Получи токен бота у @BotFather
# 3. Получи API ключ на openweathermap.org (бесплатно)

# 4. Запусти
python3 bot.py
```

## Настройка:

Создай `.env`:
```
BOT_TOKEN=твой_токен_бота
WEATHER_API_KEY=твой_ключ_openweathermap
```

## Пример использования:
```
/start
/weather Москва
/weather London
```

## Для заказа:
Напиши мне на Kwork/FL.ru — сделаю за 1 день с настройкой на твой сервер.
