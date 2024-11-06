from aiogram import types, Dispatcher
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.types.input_file import FSInputFile
from services.user_service import load_users, save_user
import logging

async def start_command(message: types.Message):
    user_id = str(message.from_user.id)
    user_first_name = message.from_user.first_name

    users = load_users()
    if user_id in users:
        welcome_message = f"С возвращением, {user_first_name}!"
    else:
        welcome_message = f"Привет, {user_first_name}! Я ваш телеграм-бот."
        save_user(user_id)

    await message.answer(welcome_message)

    # Отправка картинки с подписью
    image_path = './images/1125.jpg'  # Проверьте, что путь корректен
    caption = ('Здесь вы сможете получить пробный урок по английскому языку, пройти тестирование на уровень знаний, '
              'изучить отзывы и вызвать менеджера, чтобы задать интересующий вас вопрос и записаться на обучение.')
    try:
        photo = FSInputFile(image_path)
        await message.bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption)
    except Exception as e:
        logging.error(f"Ошибка при отправке изображения: {e}")

    # Создание кнопок
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Получить подарок", callback_data='gift')],
        [InlineKeyboardButton(text="Пройти тестирование", callback_data='test')],
        [InlineKeyboardButton(text="Подробнее о школе", callback_data='about_school')],
        [InlineKeyboardButton(text="Результаты", callback_data='results')],
        [InlineKeyboardButton(text="Отзывы", callback_data='reviews')],
        [InlineKeyboardButton(text="Программы обучения", callback_data='programs')],
        [InlineKeyboardButton(text="Вызвать менеджера", callback_data='manager')]
    ])

    await message.answer("Пожалуйста, выберите действие:", reply_markup=keyboard)

    # Создание меню-кнопки и кнопки "Мой кабинет"
    menu_keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Основное меню 🔍"), KeyboardButton(text="Мой кабинет 👤")]
        ],
        resize_keyboard=True
    )
    await message.answer("Используйте меню для навигации:", reply_markup=menu_keyboard)

def register_handlers(dp: Dispatcher):
    dp.message.register(start_command, Command('start'))
