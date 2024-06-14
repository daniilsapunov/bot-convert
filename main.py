import asyncio
from aiogram import Bot, Dispatcher, types
import openai

from .config import settings

# Инициализация бота и диспетчера
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(bot)

# Настройка OpenAI API
openai.api_key = settings.OPENAI_API_KEY
