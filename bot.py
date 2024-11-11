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

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Основное меню 🔍"), KeyboardButton(text="Мой кабинет 👤")]
    ],
    resize_keyboard=True
)

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
    
    await update.message.reply_text(message, reply_markup=menu_keyboard)
    
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

# Функция для отображения основного меню с инлайн-кнопками
async def show_main_menu(update: Update) -> None:
    keyboard = [
        [InlineKeyboardButton("Получить подарок", callback_data='gift')],
        [InlineKeyboardButton("Пройти тестирование", callback_data='test')],
        [InlineKeyboardButton("Подробнее о школе", callback_data='about_school')],
        [InlineKeyboardButton("Адреса и контакты", callback_data='contacts')],
        [InlineKeyboardButton("Отзывы", callback_data='reviews')],
        [InlineKeyboardButton("Наши услуги", callback_data='services')],
        # [InlineKeyboardButton("Вызвать менеджера", callback_data='manager')]
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
        # Отправка картинки и описания
        image_path = './images/about.jpg'
        caption = (
            "English Academy – сеть школ английского языка, которая вот уже девять лет предлагает качественное образование "
            "в сфере изучения иностранных языков. Образование, которое открывает любые двери и позволяет чувствовать уверенность в завтрашнем дне.\n\n"
            "Школы English Academy предлагают широкий выбор программ изучения английского языка для детей от 3 лет, подростков и взрослых. "
            "Программы учитывают потребности каждой категории студентов и позволяют сделать обучение не только полезным, но и максимально интересным. \n\n"
            "Занятия в English Academy проводятся по коммуникативной методике, основной задачей которой является погружение в реальную языковую среду и развитие навыков общения на иностранном языке. "
            "Это способствует эффективному освоению знаний, мотивирует к изучению английского и позволяет успешно преодолеть языковой барьер.\n\n"
            # "Пожалуйста, выберите действие:\n\n"
        )
        try:
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(chat_id=query.message.chat.id, photo=photo, caption=caption)
        except Exception as e:
            logging.error(f"Ошибка при отправке изображения: {e}")

        await show_main_menu(update)


# Проверяем, какая кнопка была нажата по значению `callback_data`
    elif query.data == 'contacts':
        await show_contacts_menu(update, context)
    elif query.data == 'kropotkin':
        await query.edit_message_text(text="г. Кропоткин, ул. Ворошилова, 1 \n\n"
                                            "Позвонить:\n"
                                            "☎️ 8-989-802-42-43 \n\n"
                                            "Написать в WhatsApp \n"
                                            "🟩 https://wa.me/79898024243 \n\n"
                                            "Перейти в VK \n"
                                            "🟦 https://vk.com/englishkropotkin \n\n"
																						"Отправить письмо: \n"
																						"📧 kropotkin@academy-english.ru ")

    elif query.data == 'armavir':
        await query.edit_message_text(text="г. Армавир, ул. Новороссийская, 91 \n\n"
                                            "Позвонить:\n"
                                            "☎️ 8-918-086-93-69 \n\n"
                                            "Написать в WhatsApp \n"
                                            "🟩 https://wa.me/79180869369 \n\n"
                                            "Перейти в VK \n"
                                            "🟦 https://vk.com/public211025348 \n\n"
																						"Отправить письмо: \n"
																						"📧 armavir@academy-english.ru ")

    elif query.data == 'reviews':
        await query.edit_message_text(text="Ознакомиться со всеми отзывами можно перейдя ниже по ссылке: \n\n"
                                            "📍 Кропоткин: \n" 
                                            "https://yandex.ru/maps/org/english_academy/83617208477/reviews/?ll=40.557228%2C45.434301&z=15 \n\n"
                                            "📍 Армавир: \n" 
                                            "https://yandex.ru/maps/org/english_academy/227095642064/reviews/?ll=41.091600%2C44.998611&z=15" )
    elif query.data == 'services':
        # Показываем меню с услугами
        await show_services_menu(update, context)
    elif query.data == 'english_courses':
        # await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/courses.jpg', 'rb'))
        await query.edit_message_text(text="Курсы английского языка English Academy рассчитаны на детей и взрослых с разным начальным уровнем подготовки. \n\n"
                                      "Наши курсы учитывают потребности каждой категории студентов и позволяют сделать обучение не только полезным, но и максимально увлекательным. Мы определим ваш текущий уровень владения языком и подберем подходящую программу после бесплатного тестирования. \n\n" 
																			"Наши курсы: \n\n"
                                      "📌 <b>Juniors Academy</b> – курс для обучения английскому языку малышей от 3 до 6 лет \n" 
                                      "📌 <b>Kids Academy</b> – курс для школьников 7-12 лет \n"
                                      "📌 <b>Teens Academy</b> – курс для подростков 13-17 лет \n"
                                      "📌 <b>Feel Fluent</b> - курсы для взрослых \n"
                                      "📌 <b>Летние курсы для детей</b> – занятия английским языком во время школьных каникул для поддержания уровня языка \n"
                                      "📌 <b>Подготовка к ОГЭ/ЕГЭ</b> – курсы по подготовке к сдаче российских экзаменов по английскому языку \n\n"
                                      "Насыщенные занятия и эффективная методика позволят освоить выбранную программу в относительно короткие сроки и гораздо увереннее общаться на английском языке. По окончании курса выдается сертификат школы с указанием уровня, который Вы прошли и баллами за итоговое тестирование.", parse_mode='HTML'
																			)

    elif query.data == 'online_courses':
        await query.edit_message_text(text="В школе English Academy вы можете заниматься английским дома, на отдыхе или во время обеденного перерыва. Все что для этого нужно - это компьютер или телефон с камерой, микрофоном и доступом в интернет.\n\n"
                                    "Занятия проводятся по коммуникативной методике с квалифицированными преподавателями и направлены на развитие всех навыков владения языком: от чтения и письма до аудирования и произношения.\n\n"
                                    "Онлайн-занятия проводятся индивидуально и в группах. Мы поможем подобрать максимально удобное для вас расписание для комфортного и эффективного изучения языка."
																		)
        # await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/online_courses.jpg', 'rb'))
        
    elif query.data == 'study_abroad':
        await query.edit_message_text(text="Что может быть лучше для практики иностранного языка, чем обучение в странах, где на этом языке говорят? Ведь поездка за рубеж – это не только способ повысить уровень владения английским языком, но также насыщенно и с пользой провести время в отпуске или на каникулах.\n\n"
                                    "English Academy предлагает индивидуальные и групповые программы для детей на каникулах, а также помогает студентам поступить в университеты Великобритании, Ирландии, Канады и США.\n\n"
                                    "Поездки с English Academy – это: \n\n"
                                    "✏️ групповая программа с сопровождением сотрудника English Academy; \n"
                                    "✏️ иностранные учебные заведения с лучшими методиками преподавания; \n"
                                    "✏️ интересные занятия английским в интернациональных группах с квалифицированными преподавателями-носителями языка; \n"
                                    "✏️ насыщенная экскурсионная программа; \n"
                                    "✏️ сертификат, подтверждающий успешное завершение программы по окончании курса. \n\n"
                                    "Такое путешествие поможет приобрести новых друзей из разных стран, преодолеть языковой барьер и попрактиковать иностранный язык в англоязычной среде."
																		)
        # await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/abroad.jpg', 'rb'))

    elif query.data == 'cambridge_center':
        await query.edit_message_text(text="Школа English Academy является открытым авторизованным центром по подготовке и приему Кембриджских экзаменов.\n\n"
                                    "Кембриджские экзамены по английскому языку созданы департаментом Кембриджского университета Cambridge Assessment English (Великобритания) для всех, кто изучает английский в качестве иностранного.\n\n"
                                    "В нашей школе вы можете подготовиться к экзамену, а в дальнейшем успешно его сдать и получить международный Кембриджский сертификат соответствующего уровня. Этот сертификат признается учебными заведениями и работодателями как реальный показатель знания языка на международном уровне. Мы принимаем экзамены для различных возрастов и целей: от подтверждения уровня знания общего курса английского языка, в том числе для детей с 7 лет, до специализированных экзаменов для преподавателей. \n\n"
                                    "<b>Школа English Academy готовит к следующим экзаменам:</b> \n\n"
                                    "🏅 YLE starters; \n"
                                    "🏅 YLE movers; \n"
                                    "🏅 YLE flyers; \n"
                                    "🏅 KET (Key); \n"
                                    "🏅 PET (Preliminary); \n"
                                    "🏅 FCE (First) \n"
                                    "🏅 CAE (Advanced) \n"
                                    "<b>Кембриджский сертификат – это:</b> \n\n"
                                    "📎 независимая и наиболее достоверная оценка знаний;\n"
                                    "📎 престижный международный сертификат, который не имеет срока давности;\n"
                                    "📎 весомый документ в портфолио ребенка;\n"
                                    "📎 возможность поступить в лучшие ВУЗы в России и за рубежом;\n"
                                    "📎 интеграция в мировую систему образования;\n"
                                    "📎 преимущество при устройстве на работу.\n\n"
                                    "Более 25 000 организаций, в числе которых школы, университеты, правительственные учреждения, частные коммерческие и государственные компании, признают его ценность, объективность отраженного в нем уровня языковой квалификации. С Кембриджским сертификатом люди идут учиться, устраиваться на работу, чувствуют себя уверенно всюду, где английский язык служит основным инструментом общения.", parse_mode='HTML'
																		)
        # await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/cambridge.jpg', 'rb'))
        
    elif query.data == 'translation_services':
        await query.edit_message_text(text="Владение английским языком в настоящее время стало обязательным условием для успешной профессиональной деятельности. Основными стратегическими целями любой компании являются развитие и совершенствование ее персонала, поэтому неотъемлемым компонентом корпоративной политики современной организации является многоуровневая система мотивации и обучения сотрудников.\n\n"
                                    "Для того, чтобы заказать перевод, Вам необходимо отправить на нашу электронную почту документ с текстом для перевода, указать язык, на который необходимо сделать перевод и отметить сроки выполнения заказа. После рассмотрения заявки с Вами свяжутся наши сотрудники и согласуют условия работы.\n\n"
																		)
        await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/translation.jpg', 'rb'))
        
    elif query.data == 'corporate_training':
        await query.edit_message_text(text="Владение английским языком в настоящее время стало обязательным условием для успешной профессиональной деятельности. Основными стратегическими целями любой компании являются развитие и совершенствование ее персонала, поэтому неотъемлемым компонентом корпоративной политики современной организации является многоуровневая система мотивации и обучения сотрудников.\n\n"
                                    "Для своих корпоративных клиентов English Academy предлагает:\n\n"
                                    "🎯 бесплатное тестирование сотрудников вашей компании для подбора программы обучения;\n"
                                    "🎯 удобное расписание занятий на базе школы;\n"
                                    "🎯 постоянный мониторинг знаний сотрудников;\n"
                                    "🎯 подбор необходимых учебных пособий в соответствии со спецификой деятельности организации;\n"
                                    "🎯 итоговый экзамен, позволяющий проверить знания сотрудников, полученные в процессе обучения;\n"
                                    "🎯 сертификат по окончании обучения, подтверждающий уровень владения иностранным языком.\n\n"
                                    "Все наши программы учитывают начальный уровень владения английским языком, а также индивидуальные требования каждого клиента."
																		)
        # await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/translation.jpg', 'rb'))
        
    elif query.data == 'primary_academy':
        await query.edit_message_text(text="Год назад мы решили открыть новое направление по дополнительным общеобразовательным программам и приглашаем детей, которые идут в 1 и 2 класс на занятия для развития знаний по математике, письму, чтению и окружающему миру.\n\n"
                                    "Преимуществами программы являются:\n\n"
                                    "- Группы маленькой наполненности, до 12 учащихся,\n"
                                    "- Продленка после занятий до 15:00,\n"
                                    "- Углубленное изучение английского языка,\n"
                                    "- Занятия шахматами и гимнастикой,\n"
                                    "- Опытные преподаватели.\n\n"
                                    "Это прекрасная возможность помочь детям углубить свои знания по основным предметам, так как у нас замечательные педагоги, сильная программа обучения и отличные результаты.\n\n"
                                    "Если вы хотите обеспечить качественное образование и достойное будущее для своего ребенка, ждём вас в нашей школе дополнительного образования!"
																		)
        # await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/translation.jpg', 'rb'))
        
    elif query.data == 'author_guides':
        await query.edit_message_text(text="<b>Пособие для обучения чтению и письму Easy Phonix</b>\n\n"
                                    "Учебные пособия зарубежных издательств по английскому языку для младших школьников предполагают умение читать, поэтому без вводного курса по чтению перейти к учебникам не представляется возможным. В этом случае пособие Easy Phonics поможет обучить детей читать и комфортно перейти к годовому учебнику. Кроме того, в программу также включено обучение письму.\n\n"
                                    "Пособие Easy Phonics направлено на обучение детей чтению и письму, может применяться для детей 6-12 лет. Книга состоит из 13 разделов и включает в себя все буквы английского алфавита и 8 основных буквосочетаний.\n\n"
                                    "Каждый раздел включает слова на вводимую букву (звук), слова на чтение, прописи для работы в классе и дома. Пособие включает 52 flash cards в формате pdf, которые можно распечатать и использовать на занятиях для презентации материала, а также карточки с алфавитом.\n\n"
                                    "Пособие было написано по современному способу обучению чтению и начинается не с первой буквы алфавита, а с буквы S, затем A и T. Буквы выбираются по их частотности появления в английских словах. Данный метод позволяет начать читать односложные слова уже на первом занятии.\n\n"
                                    "Помимо этого, нами были разработаны 5 игр (board games), которые включены в пособие и могут применяться для закрепления материала.\n\n"
                                    "Книга рассчитана на 13 занятий по 90 минут, может использоваться как отдельный курс, например летом, либо как курс по чтению в начале учебного года перед основным пособием на год.\n\n"
                                    "В комплект включены 13 подробных планов урока . Преподавателю не нужно готовиться дополнительно, все детали прописаны в планах.\n\n"
                                    "Каждый раздел пособия включает два задания на прописи (всех букв и некоторых слов). Их можно использовать как на уроках, так и в качестве домашнего задания.\n\n"
                                    "Пособие Easy Phonics было разработано методистами сети языковых школ English Academy, которые имеют 8ми летний опыт работы в сфере обучения английскому языку. Опираясь на накопленные знания, мы подобрали все необходимые материалы для быстрого и качественного освоения чтения и письма. Дизайн и иллюстрации являются авторской работой графического дизайнера и иллюстратора, поэтому наполнение выполнено в едином современном стиле.\n\n"
                                    "Пособие было выпущено в мае 2022 года и уже опробовано более чем 15 языковыми центрами , где были успешно обучены более 450 детей.\n\n"
																		"<b>Пособие для обучения чтению и письму Easy School Grammar</b>\n\n"
																		"Easy School Grammar – это второе авторское пособие в нашей сети, которое успешно работает и дает блестящие результаты нашим студентам.\n\n"
																		"Мы создали это пособие прежде всего для школ своей сети, проанализировав не только результаты наших учеников, но и рассмотрев все имеющиеся современные пособия по грамматике и ориентируясь на запрос родителей и студентов.\n\n"
																		"Работая по этому пособию, Вы получите:\n\n"
																		"- серию пособий для 2, 3, 4 классов – основной аудитории детского центра\n"
																		"- прирост клиентов – учеников начальной школы – это самая прибыльная категория учеников для частных детских учреждений\n"
																		"- возможность переводить учеников из года в год, из сезона в сезон.\n"
																		"- программу, которую можно использовать как в течение учебного года, так и на летних курсах\n"
																		"- основа программы для каждого класса – темы лексики и грамматики по требованиям ФГОС. Мы помогаем родителям, для которых важна школьная оценка.\n"
																		"- Также все 3 пособия составлены таким образом, что их можно использовать в качестве дополнительного материала к основной программе вашего центра.\n\n"
																		" Что входит в комплект?\n\n"
																		"🖊 учебное пособие типографской печати\n"
																		"🖊 подробные поурочные планы уроков для учителя (37 планов)\n"
																		"🖊 флешкарты\n"
																		"🖊 видеоурок\n\n"
																		" Курс Easy School Grammar подходит для тех, кто окончил 1 и 2 класс, но имеет пробелы по школьной программе. Темы раскрыты с учетом требований ФГОС.", parse_mode='HTML'
																	)
        # await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/translation.jpg', 'rb'))
        
    elif query.data == 'book_sales':
        await query.edit_message_text(text="Все мы знаем, как полезно читать книги на английском языке. Во-первых, это увеличивает словарный запас. Во-вторых, улучшает правописание. В-третьих, повышает самооценку. Ведь так приятно осознавать, что ты прочитал целую книгу на английском языке!\n\n"
                                    "Очень важно правильно выбрать книгу для чтения:\n\n"
                                    "- выбирайте истории, интересные именно Вам, так книга не наскучит и будет мотивация ее дочитать;\n"
                                    "- обязательно подбирайте адаптированные варианты под свой уровень английского языка;\n"
                                    "- начинайте с коротких рассказов или комиксов, постепенно переходя к более крупным литературным формам.\n\n"
                                    "В нашей школе Вы можете приобрести учебные пособия, словари и художественную литературу для студентов и преподавателей. Мы предлагаем литературу таких издательств как:\n\n"
                                    "📒 Cambridge University Press\n"
                                    "📒 Macmillan Publishers\n"
                                    "📒 Oxford University Press\n"
                                    "📒 Pearson Education\n\n"
                                    "Читать на английском — это правильно и полезно. А мы поможем подобрать вам книгу под ваш уровень."
																		)
        # await context.bot.send_photo(chat_id=query.message.chat.id, photo=open('./images/translation.jpg', 'rb'))
    
    # Добавьте другие elif блоки для других кнопок
    # elif query.data == 'manager':
    #     await query.edit_message_text(text="Вызвать менеджера: ...")
    else:
        await query.edit_message_text(text="Вы выбрали неизвестный вариант.")

# Функция для отображения меню услуг
async def show_services_menu(update: Update, context: CallbackContext) -> None:
        keyboard = [
            [InlineKeyboardButton("Курсы английского", callback_data='english_courses')],
            [InlineKeyboardButton("Онлайн курсы", callback_data='online_courses')],
            [InlineKeyboardButton("Обучение за рубежом", callback_data='study_abroad')],
            [InlineKeyboardButton("Кембриджский центр", callback_data='cambridge_center')],
            [InlineKeyboardButton("Услуги по переводу", callback_data='translation_services')],
            [InlineKeyboardButton("Корпоративное обучение", callback_data='corporate_training')],
            [InlineKeyboardButton("Начальная академия", callback_data='primary_academy')],
            [InlineKeyboardButton("Авторские пособия", callback_data='author_guides')],
            [InlineKeyboardButton("Продажа литературы", callback_data='book_sales')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Нажмите чтобы узнать подробнее об услуге:", reply_markup=reply_markup)

# Функция для отображения меню контактов
async def show_contacts_menu(update: Update, context: CallbackContext) -> None:
        keyboard = [
            [InlineKeyboardButton("Кропоткин", callback_data='kropotkin')],
            [InlineKeyboardButton("Армавир", callback_data='armavir')],
            # [InlineKeyboardButton("Пятигорск", callback_data='pyatigorsk')],
            # [InlineKeyboardButton("Прохладный", callback_data='prohladny')],
            # [InlineKeyboardButton("Нальчик", callback_data='nalchik')],
            # [InlineKeyboardButton("Владикавказ", callback_data='vladikavkaz')],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text("Нажмите чтобы узнать подробнее об услуге:", reply_markup=reply_markup)


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
        # f"🔗 Профиль: {'https://t.me/' + user.username if user.username else 'не указан'}\n"
        f"📷 Фото профиля: {photo_url if photo_url else 'не указано'}\n"
        f"📆 Время входа: {update.message.date}\n"
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
