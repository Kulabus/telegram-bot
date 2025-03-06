import aiosqlite
from aiogram import types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder
from quiz_data import quiz_data
from create_bot import dp

# Зададим имя базы данных
DB_NAME = 'quiz_bot.db'

def generate_options_keyboard(answer_options):
  # Создаем сборщика клавиатур типа Inline
    builder = InlineKeyboardBuilder()

    # В цикле создаем 4 Inline кнопки, а точнее Callback-кнопки
    for i in range(len(answer_options)):
        builder.add(types.InlineKeyboardButton(
            text=answer_options[i],
            callback_data=str(i))
        )

    # Выводим по одной кнопке в столбик
    builder.adjust(1)
    return builder.as_markup()

# Создадим таблицу в базе данных
async def create_table():
    # Создаем соединение с базой данных (если она не существует, то она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Выполняем SQL-запрос к базе данных
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state ('user_id' INTEGER PRIMARY KEY, 
                         'username' TEXT DEFAULT 'player', 
                         'first_name' TEXT DEFAULT 'player', 
                         'question_index' INTEGER, 
                         'score' INTEGER DEFAULT 0, 
                         'last_score' INTEGER DEFAULT 0)''')
        # Сохраняем изменения
        await db.commit()

# Создание или замена значений колонок user_id и question_index в таблице quiz_state
async def init_user(user_id, username, first_name, index, score, last_score):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, username, first_name, question_index, score, last_score) VALUES (?, ?, ?, ?, ?, ?)', (user_id, username, first_name, index, score, last_score))
        # Сохраняем изменения
        await db.commit()

# Создание или замена значений колонок user_id и question_index в таблице quiz_state
async def update_quiz_index(user_id, index):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('UPDATE quiz_state SET question_index = (?) WHERE user_id = (?)', (index, user_id))
        # Сохраняем изменения
        await db.commit()

async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

# Создание или замена значений колонок last_score на score в таблице quiz_state
async def update_quiz_score(user_id, score):
    # Создаем соединение с базой данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('UPDATE quiz_state SET score = (?) WHERE user_id = (?)', (score, user_id))
        # Сохраняем изменения
        await db.commit()

async def get_quiz_score(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT score FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

# Создание или замена значений колонок last_score на score в таблице quiz_state
async def update_quiz_last_score(user_id, score):
    # Создаем соединение с базой данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует
        await db.execute('UPDATE quiz_state SET last_score = (?) WHERE user_id = (?)', (score, user_id))
        # Сохраняем изменения
        await db.commit()

async def get_quiz_last_score(user_id):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT last_score FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0

# Выводим вопрос и кнопки с вариантами ответов
async def get_question(message, user_id):

    # Запрашиваем из базы текущий индекс для вопроса
    current_question_index = await get_quiz_index(user_id)
    # Получаем индекс правильного ответа для текущего вопроса
    correct_index = quiz_data[current_question_index]['correct_option']
    # Получаем список вариантов ответа для текущего вопроса
    opts = quiz_data[current_question_index]['options']

    # Функция генерации кнопок для текущего вопроса квиза
    # В качестве аргументов передаем варианты ответов и значение правильного ответа (не индекс!)
    kb = generate_options_keyboard(opts)
    # Отправляем в чат сообщение с вопросом, прикрепляем сгенерированные кнопки
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)

# Создаём новую игру
async def new_quiz(message):
    # получаем id пользователя, отправившего сообщение
    user_id = message.from_user.id
    username = message.from_user.username 
    first_name = message.from_user.first_name
    # сбрасываем значение текущего индекса вопроса квиза в 0
    current_question_index = 0
    score = 0
    last_score = await get_quiz_last_score(user_id)
    await init_user(user_id, username, first_name, current_question_index, score, last_score)

    # запрашиваем новый вопрос для квиза
    await get_question(message, user_id)

async def get_rating(message):
    async with aiosqlite.connect(DB_NAME) as db:
        async with db.execute('SELECT COALESCE(username, first_name) AS username, last_score FROM quiz_state ORDER BY last_score DESC LIMIT 10') as cursor:
            results = await cursor.fetchall()
            answer_message = "Рейтинг лидеров\n"
            for i in range(len(results)):
                answer_message += '\n%2i. %s   %d' % (i + 1, results[i][0], results[i][1])
            await message.answer(answer_message)
