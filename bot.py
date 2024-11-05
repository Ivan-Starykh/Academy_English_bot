import logging
import os
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackContext, CallbackQueryHandler

# Загрузка переменных из .env
load_dotenv()

# Вставьте ваш токен здесь
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
    
    # Отправка картинки
    image_path = './images/1125.jpg'
    try:
        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(photo=InputFile(photo))
    except Exception as e:
        logging.error(f"Ошибка при отправке изображения: {e}")
    
    # Отправка описания
    description = ('Здесь вы сможете получить пробный урок по английскому языку, пройти тестирование на уровень знаний, '
                  'изучить отзывы и вызвать менеджера, чтобы задать интересующий вас вопрос и записаться на обучение.')
    await update.message.reply_text(description)
    
    # Создание кнопок
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
    
    await update.message.reply_text("Пожалуйста, выберите действие:", reply_markup=reply_markup)

# Обработчик для кнопок
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    # Здесь можно добавить логику для обработки каждого действия
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

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button))  # Добавление обработчика для кнопок

    application.run_polling()

if __name__ == '__main__':
    main()
