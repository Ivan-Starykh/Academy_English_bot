from aiogram import types
from bot import dp, bot

@dp.callback_query(lambda callback_query: True)
async def process_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    
    if data == 'gift':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Получить подарок: ...")
    elif data == 'test':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Пройти тестирование: ...")
    elif data == 'about_school':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Подробнее о школе: ...")
    elif data == 'results':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Результаты: ...")
    elif data == 'reviews':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Отзывы: ...")
    elif data == 'programs':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Программы обучения: ...")
    elif data == 'manager':
        await bot.answer_callback_query(callback_query.id)
        await bot.send_message(callback_query.from_user.id, "Вызвать менеджера: ...")
