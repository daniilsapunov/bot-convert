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
    prompt = "Привет! Давай определим твои ценности. Например, что для тебя важно в жизни?"
    await msg.answer(prompt)


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
    user_id = message.from_user.id
    context = {}
    if user_id in context:
        context[user_id].append(message.text)
    else:
        context[user_id] = [message.text]
    # response = await get_assistant_response(question)
    # await message.reply(response)

    # voice_file_path = await text_to_speech(response)
    # voice = FSInputFile(f'{voice_file_path}')
    # await bot.send_audio(message.chat.id, voice)

    values = await ask_and_reply(message.text, user_id, context)
    print(values)
    if values is False:
        response = await generate_openai_response(message.text, context.get(user_id, []))
        await message.reply(response)
    else:
        await message.reply(f"Ваша ценность: {values[12:-3]}")
