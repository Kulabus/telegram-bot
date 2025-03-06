from aiogram import Router, F, types
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from middleware import *
from create_bot import dp
from quiz_data import quiz_data

start_router = Router()

# Хэндлер на команду /start
@start_router.message(CommandStart())
async def cmd_start(message: Message):
    # Создаем сборщика клавиатур типа Reply
    builder = ReplyKeyboardBuilder()
    # Добавляем в сборщик одну кнопку
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Рейтинговая таблица"))
    # Прикрепляем кнопки к сообщению
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))

@dp.message(F.text=="Начать игру")
@dp.message(Command("quiz"))
async def cmd_quiz(message: Message):
    # Отправляем новое сообщение без кнопок
    await message.answer(f"Давайте начнем квиз!")
    # Запускаем новый квиз
    await new_quiz(message)

@dp.message(F.text=="Рейтинговая таблица")
@dp.message(Command("score_table"))
async def cmd_score_table(message: Message):
    await get_rating(message)

@dp.callback_query(F.data.in_({'0', '1', '2', '3'}))
async def answer(callback: types.CallbackQuery):
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    answer_index = int(callback.data)
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']

    await callback.message.answer(f'Ваш ответ: {quiz_data[current_question_index]['options'][answer_index]}')

    if answer_index == correct_option:
        # Получение текущего счёта score
        current_score = await get_quiz_score(callback.from_user.id)

        # Обновляем счёт пользователя
        current_score += 1
        await update_quiz_score(callback.from_user.id, current_score)

        # Отправляем в чат сообщение, что ответ верный
        await callback.message.answer("Верно!")
    else:
        # Отправляем в чат сообщение об ошибке с указанием верного ответа
        await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index)

    # Проверяем достигнут ли конец квиза
    if current_question_index < len(quiz_data):
        # Следующий вопрос
        await get_question(callback.message, callback.from_user.id)
    else:
        # Уведомление об окончании квиза
        current_score = await get_quiz_score(callback.from_user.id)
        await update_quiz_last_score(callback.from_user.id, current_score)
        current_last_score = await get_quiz_last_score(callback.from_user.id)
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")
        await callback.message.answer(f"Количество правильных ответов {current_last_score} из 10")