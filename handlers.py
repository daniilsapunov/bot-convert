from aiogram import types, F, Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()


async def start_handler(msg: Message):
    await msg.answer(
        "Привет! Я помогу тебе преобразовать голосовое сообщение в текст! ОТправь мне голосовое сообщение!")

# @router.message()
# async def message_handler(msg: Message):
#     await msg.answer(f"Твой ID: {msg.from_user.id}")
