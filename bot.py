import logging
import os
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext

# Вставьте ваш токен здесь
TOKEN = '7880782507:AAFUjK_vuEBrj1_j3qZ9CyW-XkDFDCxDg3Y'

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

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))

    application.run_polling()

if __name__ == '__main__':
    main()
