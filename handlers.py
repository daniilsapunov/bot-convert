from openai import OpenAI, AsyncOpenAI
from aiogram import Bot, F, Router
from aiogram.types import Message, FSInputFile
from config import settings
from aiogram.filters import Command
from utils import text_to_speech, save_voice_as_mp3, audio_to_text, get_assistant_response

router = Router()

client = OpenAI(api_key=settings.OPENAI_API_KEY)
aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


@router.message(Command('start'))
async def start_handler(msg: Message):
    await msg.answer(
        "Привет! Я помогу тебе преобразовать голосовое сообщение в текст! ОТправь мне голосовое сообщение!")


@router.message(F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot):
    """Принимает голосовое сообщение, транскрибирует его в текст."""

    voice_path = await save_voice_as_mp3(bot, message.voice)
    transcripted_voice_text = await audio_to_text(voice_path)

    if transcripted_voice_text:
        await message.reply(text=transcripted_voice_text)


@router.message()
async def handle_message(message: Message, bot: Bot):
    """Обрабатывает текстовые сообщения."""
    question = message.text
    response = await get_assistant_response(question)
    await message.reply(response)

    # Преобразовать текст в речь
    voice_file_path = await text_to_speech(response)
    voice = FSInputFile(f'{voice_file_path}')
    await bot.send_audio(message.chat.id, voice)
