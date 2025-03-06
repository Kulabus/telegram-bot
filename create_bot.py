import logging
from aiogram import Bot, Dispatcher
from decouple import config

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Объект бота
bot = Bot(token=config('TOKEN'))
# Диспетчер
dp = Dispatcher()
