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


from telegram import Update
from telegram.ext import CallbackContext

async def my_cabinet(update: Update, context: CallbackContext) -> None:
    user = update.message.from_user
    chat_member = await context.bot.get_chat_member(update.message.chat_id, user.id)
    
    # Получение фотографии профиля пользователя
    photos = await context.bot.get_user_profile_photos(user.id)
    photo_url = ""
    if photos.total_count > 0:
        photo_file_id = photos.photos[0][0].file_id
        photo_file = await context.bot.get_file(photo_file_id)
        photo_url = photo_file.file_path

    user_info = (
        f"👤 Имя: {user.first_name}\n"
        f"🆔 ID: {user.id}\n"
        f"💬 Telegram: @{user.username if user.username else 'не указан'}\n"
        f"🗣️ Язык: {user.language_code}\n"
        f"🔗 Профиль: {'https://t.me/' + user.username if user.username else 'не указан'}\n"
        f"📆 Время входа: {update.message.date}\n"
        f"👥 Статус в чате: {chat_member.status}\n"
        f"📷 Фото профиля: {photo_url if photo_url else 'не указано'}"
    )
    
    await update.message.reply_text(user_info)

