import logging
import os
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters

# Загрузка переменных из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

# Файл для хранения данных пользователей
USERS_FILE = "users.txt"

# Чтение данных пользователей из файла
def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as file:
        users = {line.strip() for line in file}
    return users

# Сохранение данных пользователей в файл
def save_user(user_id):
    with open(USERS_FILE, "a") as file:
        file.write(f"{user_id}\n")

async def start(update: Update, context: CallbackContext) -> None:
    user_id = str(update.message.from_user.id)
    user_first_name = update.message.from_user.first_name
    
    users = load_users()
    
    if user_id in users:
        message = f"С возвращением, {user_first_name}!"
    else:
        message = f"Привет, {user_first_name}! Я ваш телеграм-бот."
        save_user(user_id)
    
    await update.message.reply_text(message)
    
    # Отправка картинки и описания
    image_path = './images/1125.jpg'
    caption = (
        'Здесь вы сможете получить пробный урок по английскому языку, пройти тестирование на уровень знаний, '
        'изучить отзывы и вызвать менеджера, чтобы задать интересующий вас вопрос и записаться на обучение.'
    )
    
    try:
        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(photo=InputFile(photo), caption=caption)
    except Exception as e:
        logging.error(f"Ошибка при отправке изображения: {e}")

    # Показ основного меню
    await show_main_menu(update)

    # Создание меню-кнопки и кнопки "Мой кабинет"
    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Основное меню 🔍"), KeyboardButton(text="Мой кабинет 👤")]
        ],
        resize_keyboard=True
    )
    await update.message.reply_text("Используйте меню для навигации:", reply_markup=menu_keyboard)

# Функция для отображения основного меню с инлайн-кнопками
async def show_main_menu(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton("Получить подарок", callback_data='gift')],
        [InlineKeyboardButton("Пройти тестирование", callback_data='test')],
        [InlineKeyboardButton("Подробнее о школе", callback_data='about_school')],
        [InlineKeyboardButton("Результаты", callback_data='results')],
        [InlineKeyboardButton("Отзывы", callback_data='reviews')],
        [InlineKeyboardButton("Программы обучения", callback_data='programs')],
        [InlineKeyboardButton("Вызвать менеджера", callback_data='manager')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Пожалуйста, выберите действие 🔧", reply_markup=reply_markup)

# Обработчик для кнопок
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'gift':
        await query.edit_message_text(text="Получить подарок: ...")
    elif query.data == 'test':
        await query.edit_message_text(text="Пройти тестирование: ...")
    elif query.data == 'about_school':
        await query.edit_message_text(text="Подробнее о школе: ...")
    elif query.data == 'results':
        await query.edit_message_text(text="Результаты: ...")
    elif query.data == 'reviews':
        await query.edit_message_text(text="Отзывы: ...")
    elif query.data == 'programs':
        await query.edit_message_text(text="Программы обучения: ...")
    elif query.data == 'manager':
        await query.edit_message_text(text="Вызвать менеджера: ...")

# Обработчик для текстовой кнопки "Основное меню"
async def handle_main_menu_button(update: Update, context: CallbackContext) -> None:
    if update.message.text == "Основное меню 🔍":
        await show_main_menu(update)

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(MessageHandler(filters.Text("Основное меню 🔍"), handle_main_menu_button))

    application.run_polling()

if __name__ == '__main__':
    main()








# import logging
# import os
# from aiogram import Bot, Dispatcher, types, F
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
# from aiogram.fsm.storage.memory import MemoryStorage
# from dotenv import load_dotenv
# from aiogram.filters import Command
# from aiogram.types.input_file import FSInputFile

# # Загрузка переменных из .env
# load_dotenv()
# TOKEN = os.getenv('TELEGRAM_TOKEN')

# # Инициализация бота и диспетчера
# bot = Bot(token=TOKEN)
# storage = MemoryStorage()
# dp = Dispatcher(storage=storage)

# # Настройка логирования
# logging.basicConfig(level=logging.INFO)

# # Файл для хранения данных пользователей
# USERS_FILE = 'users.txt'

# # Чтение данных пользователей из файла
# def load_users():
#     if not os.path.exists(USERS_FILE):
#         return set()
#     with open(USERS_FILE, 'r') as file:
#         users = {line.strip() for line in file}
#     return users

# # Сохранение данных пользователей в файл
# def save_user(user_id):
#     with open(USERS_FILE, 'a') as file:
#         file.write(f"{user_id}\n")

# @dp.message(Command('start'))
# async def start_command(message: types.Message):
#     user_id = str(message.from_user.id)
#     user_first_name = message.from_user.first_name
    
#     users = load_users()
    
#     if user_id in users:
#         welcome_message = f"С возвращением, {user_first_name}!"
#     else:
#         welcome_message = f"Привет, {user_first_name}! Я ваш телеграм-бот."
#         save_user(user_id)
    
#     await message.answer(welcome_message)
    
#     # Отправка картинки
#     image_path = './images/1125.jpg'  # Проверьте, что путь корректен
#     try:
#         photo = FSInputFile(image_path)
#         await bot.send_photo(chat_id=message.chat.id, photo=photo)
#     except Exception as e:
#         logging.error(f"Ошибка при отправке изображения: {e}")
    
#     # Отправка описания
#     description = ('Здесь вы сможете получить пробный урок по английскому языку, пройти тестирование на уровень знаний, '
#                    'изучить отзывы и вызвать менеджера, чтобы задать интересующий вас вопрос и записаться на обучение.')
#     await message.answer(description)
    
#     # Создание кнопок
#     keyboard = InlineKeyboardMarkup(inline_keyboard=[
#         [InlineKeyboardButton(text="Получить подарок", callback_data='gift')],
#         [InlineKeyboardButton(text="Пройти тестирование", callback_data='test')],
#         [InlineKeyboardButton(text="Подробнее о школе", callback_data='about_school')],
#         [InlineKeyboardButton(text="Результаты", callback_data='results')],
#         [InlineKeyboardButton(text="Отзывы", callback_data='reviews')],
#         [InlineKeyboardButton(text="Программы обучения", callback_data='programs')],
#         [InlineKeyboardButton(text="Вызвать менеджера", callback_data='manager')]
#     ])
    
#     await message.answer("Пожалуйста, выберите действие:", reply_markup=keyboard)

#     # Создание меню-кнопки и кнопки "Мой кабинет"
#     menu_keyboard = ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="Основное меню 🔍"), KeyboardButton(text="Мой кабинет 👤")]
#         ],
#         resize_keyboard=True
#     )
#     # await message.answer("Используйте меню для навигации:", reply_markup=menu_keyboard)

# @dp.callback_query(lambda callback_query: True)
# async def process_callback(callback_query: types.CallbackQuery):
#     data = callback_query.data
    
#     if data == 'gift':
#         await bot.answer_callback_query(callback_query.id)
#         await bot.send_message(callback_query.from_user.id, "Получить подарок: ...")
#     elif data == 'test':
#         await bot.answer_callback_query(callback_query.id)
#         await bot.send_message(callback_query.from_user.id, "Пройти тестирование: ...")
#     elif data == 'about_school':
#         await bot.answer_callback_query(callback_query.id)
#         await bot.send_message(callback_query.from_user.id, "Подробнее о школе: ...")
#     elif data == 'results':
#         await bot.answer_callback_query(callback_query.id)
#         await bot.send_message(callback_query.from_user.id, "Результаты: ...")
#     elif data == 'reviews':
#         await bot.answer_callback_query(callback_query.id)
#         await bot.send_message(callback_query.from_user.id, "Отзывы: ...")
#     elif data == 'programs':
#         await bot.answer_callback_query(callback_query.id)
#         await bot.send_message(callback_query.from_user.id, "Программы обучения: ...")
#     elif data == 'manager':
#         await bot.answer_callback_query(callback_query.id)
#         await bot.send_message(callback_query.from_user.id, "Вызвать менеджера: ...")

# async def main():
#     await dp.start_polling(bot, skip_updates=True)

# if __name__ == '__main__':
#     import asyncio
#     asyncio.run(main())


