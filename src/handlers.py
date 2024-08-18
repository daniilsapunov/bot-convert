from openai import OpenAI, AsyncOpenAI
from aiogram import Bot, F, Router
from aiogram.types import Message, FSInputFile
from config import settings
from aiogram.filters import Command
from utils import text_to_speech, save_voice_as_mp3, audio_to_text, get_assistant_response, ask_and_reply, \
    generate_openai_response
from database import async_session

router = Router()

client = OpenAI(api_key=settings.OPENAI_API_KEY)
aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


@router.message(Command('start'))
async def start_handler(msg: Message):
    await msg.answer(
        "Привет! Давай определим твои ключевые ценности. Например, "
        "что для тебя важно в жизни?"
        "Пожалуйста, напиши одну ценность:"
    )


@router.message(F.content_type == "voice")
async def process_voice_message(message: Message, bot: Bot):
    """Принимает голосовое сообщение, транскрибирует его в текст."""

    voice_path = await save_voice_as_mp3(bot, message.voice)
    transcripted_voice_text: str = await audio_to_text(voice_path)

    if transcripted_voice_text:
        await message.reply(text=transcripted_voice_text)


@router.message()
async def handle_message(message: Message, bot: Bot):
    """Обрабатывает текстовые сообщения."""
    context = {}
    question = message.text
    # response = await get_assistant_response(question)
    # await message.reply(response)

    # Преобразовать текст в речь
    # voice_file_path = await text_to_speech(response)
    # voice = FSInputFile(f'{voice_file_path}')
    # await bot.send_audio(message.chat.id, voice)

    # Выяснить ценность пользователя
    values = await ask_and_reply(question, message.from_user.id, context)

    if message.from_user.id in context:
        context[message.from_user.id].append(question)
    else:
        context[message.from_user.id] = [question]

    if values:
        await message.reply(f"Ваша ценность: {values}")
    else:
        # Используйте OpenAI для продолжения диалога
        response = await generate_openai_response(question, context)
        await message.reply(response)
