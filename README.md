telegram-bot/
├── .env
├── users.txt
├── bot.py
├── README.md
├── requirements.txt
└── src/
    ├── __init__.py
    ├── handlers.py
    ├── utils.py
    ├── config.py
    ├── images/
    │   └── 512.jpg
    └── templates/
        ├── welcome_message.txt
        └── help_message.txt


import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv
from aiogram.filters import Command
from aiogram.types.input_file import FSInputFile

# Загрузка переменных из .env
load_dotenv()
TOKEN = os.getenv('TELEGRAM_TOKEN')

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Файл для хранения данных пользователей и теста
USERS_FILE = 'users.txt'
TEST_FILE = './templates/test.txt'

# Чтение данных пользователей из файла
def load_users():
    if not os.path.exists(USERS_FILE):
        return set()
    with open(USERS_FILE, 'r') as file:
        users = {line.strip() for line in file}
    return users

# Сохранение данных пользователей в файл
def save_user(user_id):
    with open(USERS_FILE, 'a') as file:
        file.write(f"{user_id}\n")

# Загрузка вопросов теста из файла
def load_test():
    if not os.path.exists(TEST_FILE):
        return []
    with open(TEST_FILE, 'r') as file:
        questions = [line.strip() for line in file]
    return questions

# Состояния для теста
class TestStates(StatesGroup):
    question = State()

@dp.message(Command('start'))
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
        await bot.send_photo(chat_id=message.chat.id, photo=photo, caption=caption)
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

@dp.callback_query_handler(lambda c: c.data == 'test')
async def start_test(callback_query: types.CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    questions = load_test()
    if questions:
        await state.update_data(questions=questions, current_question=0, correct_answers=0)
        await ask_question(callback_query.message, state)
    else:
        await callback_query.message.answer("Вопросы для теста не найдены.")

async def ask_question(message: types.Message, state: FSMContext):
    data = await state.get_data()
    questions = data.get('questions')
    current_question = data.get('current_question')

    if current_question < len(questions):
        question = questions[current_question]
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Ответ 1", callback_data='answer1')],
            [InlineKeyboardButton(text="Ответ 2", callback_data='answer2')],
            [InlineKeyboardButton(text="Ответ 3", callback_data='answer3')],
            [InlineKeyboardButton(text="Ответ 4", callback_data='answer4')]
        ])
        await message.answer(question, reply_markup=keyboard)
        await state.set_state(TestStates.question)
    else:
        await message.answer("Тест завершен. Спасибо за участие!")

@dp.callback_query_handler(lambda c: c.data.startswith('answer'))
async def handle_answer(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    current_question = data.get('current_question')
    correct_answers = data.get('correct_answers')

    # Здесь можно добавить проверку правильности ответа

    await state.update_data(current_question=current_question + 1, correct_answers=correct_answers)
    await ask_question(callback_query.message, state)

@dp.message(Command('menu'))
async def show_menu(message: types.Message):
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Запустить"), KeyboardButton(text="/start")],
            [KeyboardButton(text="Помощь"), KeyboardButton(text="/help")]
        ],
        resize_keyboard=True
    )
    await message.answer("Меню", reply_markup=keyboard)

async def main():
    await dp.start_polling(bot, skip_updates=True)

if __name__ == '__main__':
    import asyncio
