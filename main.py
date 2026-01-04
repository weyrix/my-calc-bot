import asyncio
import logging
import os
import sys

# Проверка на наличие библиотеки aiogram
try:
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from aiogram.exceptions import TelegramBadRequest
except ImportError:
    sys.exit("Ошибка: Не установлена библиотека aiogram. В requirements.txt должно быть написано: aiogram>=3.0.0")

# --- НАСТРОЙКИ ---
# Если запускаешь на ПК, можешь вставить токен прямо сюда вместо os.getenv...
# Но для Heroku оставь как есть и задай переменную в настройках сайта!
BOT_TOKEN = os.getenv("BOT_TOKEN") 

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- КЛАВИАТУРА КАЛЬКУЛЯТОРА ---
def get_keyboard():
    # Раскладка кнопок
    buttons_layout = [
        ["C", "<", "/", "*"],
        ["7", "8", "9", "-"],
        ["4", "5", "6", "+"],
        ["1", "2", "3", "="],
        ["0", "."] # Последний ряд
    ]
    
    keyboard = []
    for row in buttons_layout:
        row_btns = []
        for text in row:
            # action - это то, что бот получит при нажатии
            action = "clear" if text == "C" else "back" if text == "<" else text
            row_btns.append(InlineKeyboardButton(text=text, callback_data=action))
        keyboard.append(row_btns)
        
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# --- START ---
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "🧮 <b>Калькулятор готов!</b>\nЖми на кнопки:", 
        reply_markup=get_keyboard(),
        parse_mode="HTML"
    )

# --- ЛОГИКА ---
@dp.callback_query()
async def callback_calc(callback: types.CallbackQuery):
    action = callback.data
    text = callback.message.text
    
    # Убираем лишний текст из сообщения, если он там был (оставляем только цифры/пример)
    if "Калькулятор" in text:
        text = "0"

    new_text = text

    if action == "clear":
        new_text = "0"
    
    elif action == "back":
        new_text = text[:-1]
        if not new_text: new_text = "0"

    elif action == "=":
        try:
            # Считаем выражение
            # Заменяем визуальные символы на программные, если нужно (тут они совпадают)
            result = str(eval(text))
            new_text = result
        except Exception:
            new_text = "Error" # Если деление на ноль или бред
            
    else:
        # Если нажали цифру или знак
        if text == "0" or text == "Error" or text == "🧮 Калькулятор готов!":
            new_text = action
        else:
            new_text += action

    # Редактируем сообщение, только если текст изменился
    if new_text != text:
        try:
            await callback.message.edit_text(new_text, reply_markup=get_keyboard())
        except TelegramBadRequest:
            await callback.answer() # Просто гасим часики загрузки

    await callback.answer()

# --- ЗАПУСК ---
async def main():
    if not BOT_TOKEN:
        sys.exit("Ошибка: Токен бота не найден. Укажи BOT_TOKEN в Config Vars на Heroku.")
        
    print("Бот запущен...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
