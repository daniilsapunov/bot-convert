import asyncio
import logging
import io

from openai import OpenAI, AsyncOpenAI

client = OpenAI(api_key=settings.OPENAI_API_KEY)
aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
from pydub import AudioSegment
from aiogram import Bot, Dispatcher, F, Router
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Voice, Message, Audio
from typing import Tuple
from config import settings
from aiogram.filters import Command

router = Router()


@router.message(Command('start'))
async def start_handler(msg: Message):
    await msg.answer(
        "Привет! Я помогу тебе преобразовать голосовое сообщение в текст! ОТправь мне голосовое сообщение!")


bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())



async def main():
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def audio_to_text(file_path: str) -> str:
    """Принимает путь к аудио файлу, возвращает текст файла."""
    with open(file_path, "rb") as audio_file:
        transcript = await aclient.audio.transcribe("whisper-1", audio_file)
    return transcript["text"]


async def save_voice_as_mp3(bot: Bot, voice: Voice) -> str:
    """Скачивает голосовое сообщение и сохраняет в формате mp3."""
    voice_file_info = await bot.get_file(voice.file_id)
    voice_ogg = io.BytesIO()
    await bot.download_file(voice_file_info.file_path, voice_ogg)
    voice_mp3_path = f"voice_files/voice-{voice.file_unique_id}.mp3"
    AudioSegment.from_file(voice_ogg, format="ogg").export(
        voice_mp3_path, format="mp3"
    )
    return voice_mp3_path


@router.message(F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot):
    """Принимает голосовое сообщение, транскрибирует его в текст."""

    voice_path = await save_voice_as_mp3(bot, message.voice)
    transcripted_voice_text = await audio_to_text(voice_path)

    if transcripted_voice_text:
        await message.reply(text=transcripted_voice_text)


async def get_assistant_response(question: str) -> str:
    """Получает ответ от OpenAI Assistant API на заданный вопрос."""
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Или другая подходящая модель Assistant API
    messages=[
        {"role": "user", "content": question}
    ],
    temperature=0.7,  # Уровень креативности (0 - минимальный, 1 - максимальный)
    max_tokens=1000)
    return response.choices[0].message.content


async def text_to_speech(text: str) -> Tuple[str, str]:
    """Преобразует текст в речь с помощью OpenAI TTS API"""
    response = await openai.Audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    voice_data = response.content
    voice_file_path = "voice_files/response.mp3"
    with open(voice_file_path, "wb") as f:
        f.write(voice_data)
    return voice_file_path, response.headers.get('Content-Type', 'audio/mpeg')


@router.message()
async def handle_message(message: Message):
    """Обрабатывает текстовые сообщения."""
    question = message.text
    response = await get_assistant_response(question)
    await message.reply(response)

    # Преобразовать текст в речь
    voice_file_path, content_type = await text_to_speech(response)

    # Отправить голосовое сообщение
    await message.reply_audio(
        Audio(source=voice_file_path, mime_type=content_type)
    )


# @router.message()
# async def handle_message(message: Message):
#     """Обрабатывает текстовые сообщения."""
#     question = message.text
#     response = await get_assistant_response(question)
#     await message.reply(response)
#

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
