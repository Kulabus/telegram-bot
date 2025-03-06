import asyncio
from create_bot import bot, dp
from handlers import start_router
from middleware import create_table

async def main():
    dp.include_router(start_router)
    # Запускаем создание таблицы базы данных
    await create_table()
    # Запускаем поллинг (опрос) бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
