import logging
import os
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
from telegram.error import BadRequest

# Загрузка переменных из .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

logging.basicConfig(level=logging.INFO)

# Файл для хранения данных пользователей и отправленных подарков
USERS_FILE = "users.txt"
GIFTED_USERS_FILE = "gifted_users.txt"

# Чтение данных пользователей из файла
def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, "r") as file:
        users = {line.strip() for line in file}
    return users

# Чтение данных пользователей, которым уже отправлен подарок
def load_gifted_users():
    if not os.path.exists(GIFTED_USERS_FILE):
        return set()
    with open(GIFTED_USERS_FILE, "r") as file:
        users = {line.strip() for line in file}
    return users

# Сохранение данных пользователей в файл
def save_user(user_id):
    with open(USERS_FILE, "a") as file:
        file.write(f"{user_id}\n")

# Сохранение данных пользователей, которым отправлен подарок
def save_gifted_user(user_id):
    with open(GIFTED_USERS_FILE, "a") as file:
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
    # await update.message.reply_text("Используйте меню для навигации:", reply_markup=menu_keyboard)

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

# Обработчик для текстовой кнопки "Основное меню"
async def handle_main_menu_button(update: Update, context: CallbackContext) -> None:
    if update.message.text == "Основное меню 🔍":
        await show_main_menu(update)

CHANNEL_USERNAME = "@academyenglishstart"  

# Обработчик для инлайн-кнопок
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'gift':
        user_id = query.from_user.id
        # Проверка, получал ли уже пользователь подарок
        if user_has_received_gift(user_id):
            await query.edit_message_text(text="Вы уже получили свой подарок.")
        else:
            message = (
                "Для получения подарка необходимо быть подписанным на Телеграм-канал.\n\n"
                "👉 @academyenglishstart\n\n"
                "И нажать кнопку \"Подписался\" под этим постом."
            )
            # Создание инлайн-кнопки "Подписался"
            keyboard = [[InlineKeyboardButton("Подписался", callback_data='subscribed')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=message, reply_markup=reply_markup)

    elif query.data == 'subscribed':
        user_id = query.from_user.id
        try:
            # Проверка статуса пользователя в канале
            chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
            if chat_member.status in ["member", "administrator", "creator"]:
                # Пользователь подписан
                await query.edit_message_text(text="Спасибо за подписку! Теперь вы можете получить подарок.")
                # Отправка подарка
                await send_gift(context.bot, user_id)
            else:
                # Пользователь не подписан
                message = "Вы не подписались на канал: @academyenglishstart"
								# Создание инлайн-кнопки "Подписался"
                keyboard = [[InlineKeyboardButton("Подписался", callback_data='subscribed')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=message, reply_markup=reply_markup)
        except BadRequest:
            # Если бот не администратор канала или канал не найден
            await query.edit_message_text(text="Ошибка: невозможно проверить подписку.")

    # Обработка нажатия на разные кнопки
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

# Проверка, получал ли пользователь подарок
def user_has_received_gift(user_id):
    RECEIVED_GIFTS_FILE = "received_gifts.txt"
    if not os.path.exists(RECEIVED_GIFTS_FILE):
        return False
    with open(RECEIVED_GIFTS_FILE, "r") as file:
        users = {line.strip() for line in file}
    return str(user_id) in users

# Сохранение информации о получении подарка
def save_gift_receipt(user_id):
    RECEIVED_GIFTS_FILE = "received_gifts.txt"
    with open(RECEIVED_GIFTS_FILE, "a") as file:
        file.write(f"{user_id}\n")

# Отправка подарка пользователю
async def send_gift(bot, user_id):
    # Пример отправки PDF-файлов
    files = ["./Unit 2 Progress Test.pdf", "./Ready_Unit 2 Progress Test.pdf"]
    for file_path in files:
        try:
            with open(file_path, "rb") as file:
                await bot.send_document(chat_id=user_id, document=InputFile(file))
        except Exception as e:
            logging.error(f"Ошибка при отправке файла {file_path}: {e}")

    # Сохранение информации о получении подарка
    save_gift_receipt(user_id)
    
async def my_cabinet(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    user_info = (
        f"👤 Имя: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"💬 Telegram: @{user.username if user.username else 'не указан'}"
    )
    
    # Проверка подписки на канал
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
        if member.status in ['member', 'administrator', 'creator']:
            subscription_status = "✅ Подписан на канал"
        else:
            subscription_status = "❌ Не подписан на канал @academyenglishstart"
    except BadRequest:
        subscription_status = "❌ Не подписан на канал @academyenglishstart"
    
    # Отправка информации о пользователе и статусе подписки
    await update.message.reply_text(f"{user_info}\n{subscription_status}")


# Основная функция
def main():
    application = Application.builder().token(TOKEN).build()
    # Обработчик для команды /start
    application.add_handler(CommandHandler("start", start))
    # Обработчик для инлайн-кнопок
    application.add_handler(CallbackQueryHandler(button))
    # Обработчик для кнопки "Основное меню"
    application.add_handler(MessageHandler(filters.Text(["Основное меню 🔍"]), handle_main_menu_button))
    # Обработчик для кнопки "Мой кабинет", который вызывает функцию my_cabinet
    application.add_handler(MessageHandler(filters.Text(["Мой кабинет 👤"]), my_cabinet))
    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()

# import logging
# import os
# from dotenv import load_dotenv
# from telegram import (
#     Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile,
#     ReplyKeyboardMarkup, KeyboardButton
# )
# from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler, MessageHandler, filters
# from telegram.error import BadRequest

# # Загрузка переменных из .env
# load_dotenv()
# TOKEN = os.getenv("TELEGRAM_TOKEN")

# logging.basicConfig(level=logging.INFO)

# # Файл для хранения данных пользователей
# USERS_FILE = "users.txt"

# # Чтение данных пользователей из файла
# def load_users():
#     if not os.path.exists(USERS_FILE):
#         return set()
#     with open(USERS_FILE, "r") as file:
#         users = {line.strip() for line in file}
#     return users

# # Сохранение данных пользователей в файл
# def save_user(user_id):
#     with open(USERS_FILE, "a") as file:
#         file.write(f"{user_id}\n")

# async def start(update: Update, context: CallbackContext) -> None:
#     user_id = str(update.message.from_user.id)
#     user_first_name = update.message.from_user.first_name
    
#     users = load_users()
    
#     if user_id in users:
#         message = f"С возвращением, {user_first_name}!"
#     else:
#         message = f"Привет, {user_first_name}! Я ваш телеграм-бот."
#         save_user(user_id)
    
#     await update.message.reply_text(message)
    
#     # Отправка картинки и описания
#     image_path = './images/1125.jpg'
#     caption = (
#         'Здесь вы сможете получить пробный урок по английскому языку, пройти тестирование на уровень знаний, '
#         'изучить отзывы и вызвать менеджера, чтобы задать интересующий вас вопрос и записаться на обучение.'
#     )
    
#     try:
#         with open(image_path, 'rb') as photo:
#             await update.message.reply_photo(photo=InputFile(photo), caption=caption)
#     except Exception as e:
#         logging.error(f"Ошибка при отправке изображения: {e}")

#     # Показ основного меню
#     await show_main_menu(update)

#     # Создание меню-кнопки и кнопки "Мой кабинет"
#     menu_keyboard = ReplyKeyboardMarkup(
#         keyboard=[
#             [KeyboardButton(text="Основное меню 🔍"), KeyboardButton(text="Мой кабинет 👤")]
#         ],
#         resize_keyboard=True
#     )
#     await update.message.reply_text("Используйте меню для навигации:", reply_markup=menu_keyboard)

# # Функция для отображения основного меню с инлайн-кнопками
# async def show_main_menu(update: Update) -> None:
#     keyboard = [
#         [InlineKeyboardButton("Получить подарок", callback_data='gift')],
#         [InlineKeyboardButton("Пройти тестирование", callback_data='test')],
#         [InlineKeyboardButton("Подробнее о школе", callback_data='about_school')],
#         [InlineKeyboardButton("Результаты", callback_data='results')],
#         [InlineKeyboardButton("Отзывы", callback_data='reviews')],
#         [InlineKeyboardButton("Программы обучения", callback_data='programs')],
#         [InlineKeyboardButton("Вызвать менеджера", callback_data='manager')]
#     ]
#     reply_markup = InlineKeyboardMarkup(keyboard)
#     await update.message.reply_text("Пожалуйста, выберите действие 🔧", reply_markup=reply_markup)

# # Обработчик для кнопок
# async def button(update: Update, context: CallbackContext) -> None:
#     query = update.callback_query
#     await query.answer()

# # Обработка нажатия на разные кнопки
#     if query.data == 'gift':
#         message = (
#             "Для получения подарка необходимо быть подписанным на Телеграм-канал.\n\n"
#             "👉 @academyenglishstart\n\n"
#             "И нажать кнопку \"Подписался\" под этим постом."
#         )
        
#         # Создание инлайн-кнопки "Подписался"
#         keyboard = [[InlineKeyboardButton("Подписался", callback_data='subscribed')]]
#         reply_markup = InlineKeyboardMarkup(keyboard)
        
#         await query.edit_message_text(text=message, reply_markup=reply_markup)

#     elif query.data == 'test':
#         await query.edit_message_text(text="Пройти тестирование: ...")
#     elif query.data == 'about_school':
#         await query.edit_message_text(text="Подробнее о школе: ...")
#     elif query.data == 'results':
#         await query.edit_message_text(text="Результаты: ...")
#     elif query.data == 'reviews':
#         await query.edit_message_text(text="Отзывы: ...")
#     elif query.data == 'programs':
#         await query.edit_message_text(text="Программы обучения: ...")
#     elif query.data == 'manager':
#         await query.edit_message_text(text="Вызвать менеджера: ...")

#     elif query.data == 'subscribed':
#         user_id = query.from_user.id
#         try:
#             # Проверка статуса пользователя в канале
#             chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
#             if chat_member.status in ["member", "administrator", "creator"]:
#                 # Пользователь подписан
#                 await query.edit_message_text(text="✅ Спасибо за подписку! Теперь вы можете получить подарок.")
#             else:
#                 # Пользователь не подписан
#                 await query.edit_message_text(text="❌ Вы не подписались на канал @academyenglishstart")
#         except BadRequest:
#             # Если бот не администратор канала или канал не найден
#             await query.edit_message_text(text="Ошибка: невозможно проверить подписку.")
# # Обработчик для текстовой кнопки "Основное меню"
# async def handle_main_menu_button(update: Update, context: CallbackContext) -> None:
#     if update.message.text == "Основное меню 🔍":
#         await show_main_menu(update)

# CHANNEL_USERNAME = "@academyenglishstart"

# async def my_cabinet(update: Update, context: CallbackContext) -> None:
#     user = update.message.from_user
#     user_info = (
#         f"👤 Имя: {user.first_name}\n"
#         f"🆔 ID: {user.id}\n"
#         f"💬 Telegram: @{user.username if user.username else 'не указан'}"
#     )
    
#     # # Проверка подписки на канал
#     # try:
#     #     member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user.id)
#     #     if member.status in ['member', 'administrator', 'creator']:
#     #         subscription_status = "✅ Подписан на канал"
#     #     else:
#     #         subscription_status = "❌ Не подписан на канал @academyenglishstart"
#     # except BadRequest:
#     #     subscription_status = "❌ Не подписан на канал "
    
#     # await update.message.reply_text(f"{user_info}\n{subscription_status}")

# def main():
#     application = Application.builder().token(TOKEN).build()

#     # Обработчик для команды /start
#     application.add_handler(CommandHandler("start", start))
    
#     # Обработчик для инлайн-кнопок
#     application.add_handler(CallbackQueryHandler(button))

#     # Обработчик для кнопки "Основное меню"
#     application.add_handler(MessageHandler(filters.Text(["Основное меню 🔍"]), handle_main_menu_button))

#     # Обработчик для кнопки "Мой кабинет", который вызывает функцию my_cabinet
#     application.add_handler(MessageHandler(filters.Text(["Мой кабинет 👤"]), my_cabinet))

#     # Запуск бота
#     application.run_polling()

# if __name__ == '__main__':
#     main()







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


