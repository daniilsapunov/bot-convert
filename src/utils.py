from functools import partial, wraps
import io
import os
import sqlalchemy
from pydub import AudioSegment
from openai import OpenAI, AsyncOpenAI
from aiogram import Bot
from aiogram.types import Voice
from config import settings
import uuid
from models import User
from database import async_session

client = OpenAI(api_key=settings.OPENAI_API_KEY)
aclient = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


async def audio_to_text(file_path: str) -> str:
    """Принимает путь к аудио файлу, возвращает текст файла."""
    with open(file_path, "rb") as audio_file:
        transcript = await aclient.audio.transcriptions.create(model="whisper-1", file=audio_file)
    return transcript.text


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


async def text_to_speech(text: str) -> str:
    """Преобразует текст в речь с помощью OpenAI TTS API"""
    filename = f'voice_output/{str(uuid.uuid4())}' + ".ogg"
    with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text,
            response_format='aac'
    ) as response:
        response.stream_to_file(filename)
    voice_file_path = os.path.join(filename)
    return voice_file_path


async def get_assistant_response(question: str) -> str:
    """Получает ответ от OpenAI Assistant API на заданный вопрос."""
    response = client.chat.completions.create(model="gpt-3.5-turbo",  # Или другая подходящая модель Assistant API
                                              messages=[
                                                  {"role": "user", "content": question}
                                              ],
                                              temperature=0.7,
                                              # Уровень креативности (0 - минимальный, 1 - максимальный)
                                              max_tokens=1000)
    return response.choices[0].message.content


async def save_value(telegram_id, values):
    validation_response = client.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "user",
             "content": f"Does this answer contain any nonsense or inaccuracies? Answer True or False:\n{values}"}
        ],
        max_tokens=10,
        temperature=0.0,
    )

    if validation_response.choices[0].message.content.strip().lower() == "false":
        async with async_session() as session:
            stmt = (
                sqlalchemy.select(User)
                .where(User.telegram_id == telegram_id)
            )
            result = await session.execute(stmt)
            if result.scalars().one_or_none():
                stmt = (
                    sqlalchemy.update(User)
                    .where(User.telegram_id == telegram_id)
                    .values(values=values)
                    .returning(User)
                )
                await session.execute(stmt)
                await session.commit()
                return True
            else:
                user = User(telegram_id=telegram_id, values=values)
                session.add(user)
                await session.commit()
                return True
    else:
        return False


functions = [
    {
        "name": "save_value",
        "description": "Verifies the validity of the value. True or False",
        "parameters": {
            "type": "object",
            "properties": {
                "value": {
                    "type": "string",
                    "description": "User Defined Value",
                },
            },
            "required": ["value"],
        },
    }
]


async def ask_and_reply(prompt, telegram_id, context):
    # Проверяем, есть ли контекст для данного пользователя
    if telegram_id in context:
        # Добавляем предыдущие сообщения в качестве контекста
        context_messages = [{"role": "user", "content": msg} for msg in context[telegram_id]]
        messages = context_messages + [{"role": "user", "content": prompt}]
    else:
        messages = [{"role": "user", "content": prompt}]

    completion = await aclient.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        function_call="auto",
    )
    output = completion.choices[0]

    try:
        if output.message.function_call.name == "save_value":
            if completion.choices[0].message.function_call.arguments:
                await save_value(telegram_id, completion.choices[0].message.function_call.arguments[12:-3])
            return completion.choices[0].message.function_call.arguments
    except (AttributeError, IndexError) as e:
        print(f"Ошибка: {e}")
        # Продолжаем диалог, пытаясь получить ответ от модели
        try:
            response = output.message.content.strip()
            return response
        except (AttributeError, IndexError) as e:
            print(f"Ошибка: {e}")
            return "Извините, произошла ошибка. Я не могу продолжить диалог."


async def generate_openai_response(prompt, context):

    print(prompt)
    print(context)
    completion = await aclient.chat.completions.create(
        model="gpt-3.5-turbo-0613",
        messages=[
            {"role": "system", "content": context},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return completion.choices[0].message.content.strip()
