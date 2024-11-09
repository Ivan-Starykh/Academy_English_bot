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

    elif query.data == 'about_school':
        # Отправка картинки и описания
        image_path = './images/about.jpg'
        caption = (
            "English Academy – сеть школ английского языка, которая вот уже девять лет предлагает качественное образование "
            "в сфере изучения иностранных языков. Образование, которое открывает любые двери и позволяет чувствовать уверенность в завтрашнем дне.\n\n"
            "Школы English Academy предлагают широкий выбор программ изучения английского языка для детей от 3 лет, подростков и взрослых. "
            "Программы учитывают потребности каждой категории студентов и позволяют сделать обучение не только полезным, но и максимально интересным. "
            "Занятия в English Academy проводятся по коммуникативной методике, основной задачей которой является погружение в реальную языковую среду и развитие навыков общения на иностранном языке. "
            "Это способствует эффективному освоению знаний, мотивирует к изучению английского и позволяет успешно преодолеть языковой барьер.\n\n"
            "Пожалуйста, выберите действие:\n\n"
        )
        try:
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(chat_id=query.message.chat.id, photo=photo, caption=caption)
        except Exception as e:
            logging.error(f"Ошибка при отправке изображения: {e}")

        await show_main_menu(update)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'gift':
        user_id = query.from_user.id
        if user_has_received_gift(user_id):
            await query.edit_message_text(text="Вы уже получили свой подарок.")
        else:
            message = (
                "Для получения подарка необходимо быть подписанным на Телеграм-канал.\n\n"
                "👉 @academyenglishstart\n\n"
                "И нажать кнопку \"Подписался\" под этим постом."
            )
            keyboard = [[InlineKeyboardButton("Подписался", callback_data='subscribed')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=message, reply_markup=reply_markup)

    elif query.data == 'subscribed':
        user_id = query.from_user.id
        try:
            chat_member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
            if chat_member.status in ["member", "administrator", "creator"]:
                await query.edit_message_text(text="Спасибо за подписку! Теперь вы можете получить подарок.")
                await send_gift(context.bot, user_id)
            else:
                message = "Вы не подписались на канал: @academyenglishstart"
                keyboard = [[InlineKeyboardButton("Подписался", callback_data='subscribed')]]
                reply_markup = InlineKeyboardMarkup(keyboard)
                await query.edit_message_text(text=message, reply_markup=reply_markup)
        except BadRequest:
            await query.edit_message_text(text="Ошибка: невозможно проверить подписку.")

    elif query.data == 'about_school':
        image_path = './images/about.jpg'
        caption = (
            "English Academy – сеть школ английского языка, которая вот уже девять лет предлагает качественное образование "
            "в сфере изучения иностранных языков. Образование, которое открывает любые двери и позволяет чувствовать уверенность в завтрашнем дне.\n\n"
            "Школы English Academy предлагают широкий выбор программ изучения английского языка для детей от 3 лет, подростков и взрослых. "
            "Программы учитывают потребности каждой категории студентов и позволяют сделать обучение не только полезным, но и максимально интересным. "
            "Занятия в English Academy проводятся по коммуникативной методике, основной задачей которой является погружение в реальную языковую среду и развитие навыков общения на иностранном языке. "
            "Это способствует эффективному освоению знаний, мотивирует к изучению английского и позволяет успешно преодолеть языковой барьер.\n\n"
            "Пожалуйста, выберите действие:\n\n"
        )
        try:
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(chat_id=query.message.chat.id, photo=photo, caption=caption)
        except Exception as e:
            logging.error(f"Ошибка при отправке изображения: {e}")

        await show_main_menu(update)

    elif query.data == 'services':
        message = (
            "Мы предлгаем следующие виды услуг:\n\n"
            "👉 Курсы английского\n"
            "Групповые и индивидуальные занятия для детей, подростков и взрослых.\n\n"
            "👉 Онлайн курсы\n"
            "Доступное дистанционное онлайн-обучение на платформе Zoom\n\n"
            "👉 Обучение за рубежом\n"
            "Курсы английского языка в лучших колледжах и университетах мира.\n\n"
            "👉 Кембриджский центр\n"
            "Подготовка и сдача Кембриджских экзаменов.\n\n"
            "👉 Услуги по переводу\n"
            "Все виды письменных и устных переводов на английский и немецкий языки.\n\n"
            "👉 Корпоративное обучение\n"
            "Языковое обучение для ваших сотрудников на базе школы.\n\n"
            "👉 Начальная академия\n"
            "Обучение по дополнительным общеобразовательным программам для детей 1 и 2 класса, находящихся на семейном образовании.\n\n"
            "👉 Авторские пособия для преподавателей\n"
            "Пособия для обучения детей чтению, письму и грамматике.\n\n"
            "👉 Продажа литературы\n"
            "Учебная и художественная литература ведущих британских издательств.\n\n"
        )
        keyboard = [
            [InlineKeyboardButton("Узнать подробнее о курсах английского", callback_data='detail_english_courses')],
            [InlineKeyboardButton("Узнать подробнее об онлайн курсах", callback_data='detail_online_courses')],
            [InlineKeyboardButton("Узнать подробнее об обучении за рубежом", callback_data='detail_abroad')],
            [InlineKeyboardButton("Узнать подробнее о кембриджском центре", callback_data='detail_cambridge')],
            [InlineKeyboardButton("Узнать подробнее об услугах по переводу", callback_data='detail_translation')],
            [InlineKeyboardButton("Узнать подробнее о корпоративном обучении", callback_data='detail_corporate')],
            [InlineKeyboardButton("Узнать подробнее о начальной академии", callback_data='detail_primary_academy')],
            [InlineKeyboardButton("Узнать подробнее об авторских пособиях", callback_data='detail_authors_guides')],
            [InlineKeyboardButton("Узнать подробнее о продаже литературы", callback_data='detail_book_sales')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(text=message, reply_markup=reply_markup)

    elif query.data == 'detail_english_courses':
        await query.edit_message_text(text="Групповые и индивидуальные занятия для детей, подростков и взрослых. \n\nКартинка: (здесь можно добавить изображение)")
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/english_courses.jpg', 'rb'))

    elif query.data == 'detail_online_courses':
        await query.edit_message_text(text="Доступное дистанционное онлайн-обучение на платформе Zoom. \n\nКартинка: (здесь можно добавить изображение)")
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/online_courses.jpg', 'rb'))

    elif query.data == 'detail_abroad':
        await query.edit_message_text(text="Курсы английского языка в лучших колледжах и университетах мира. \n\nКартинка: (здесь можно добавить изображение)")
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/abroad.jpg', 'rb'))

    elif query.data == 'detail_cambridge':
        await query.edit_message_text(text="Подготовка и сдача Кембриджских экзаменов. \n\nКартинка: (здесь можно добавить изображение)")
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/cambridge.jpg', 'rb'))

    elif query.data == 'detail_translation':
        await query.edit_message_text(text="Все виды письменных и устных переводов на английский и немецкий языки. \n\nКартинка: (здесь можно добавить изображение)")
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/translation.jpg', 'rb'))

    elif query.data == 'detail_corporate':
        await query.edit_message_text(text="Языковое обучение для ваших сотрудников на базе школы. \n\nКартинка: (здесь можно добавить изображение)")
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/corporate_training.jpg', 'rb'))

    elif query.data == 'detail_primary_academy':
        await query.edit_message_text(text="Обучение по дополнительным общеобразовательным программам для детей 1 и 2 класса, находящихся на