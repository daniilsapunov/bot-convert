import io
import os
from pydub import AudioSegment
from openai import OpenAI, AsyncOpenAI
from aiogram import Bot
from aiogram.types import Voice
from src.config import settings
import uuid

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


# @functools.partial(client.chat.completions.create, model="gpt-3.5-turbo")
# def validate_value(value):
#     response = client.chat.completions.create(
#         messages=[
#             {
#                 "role": "user",
#                 "content": f"Валидируй эту ценность: {value} - верни True, если она корректная, иначе False",
#             }
#         ],
#         functions=[
#             {
#                 "name": "validate",
#                 "description": "Проверяет, является ли ценность корректной.",
#                 "parameters": {
#                     "type": "object",
#                     "properties": {
#                         "result": {
#                             "type": "boolean",
#                             "description": "True, если ценность корректная, иначе False",
#                         },
#                     },
#                     "required": ["result"],
#                 },
#             }
#         ],
#     )
#
#     function_call = response["choices"][0]["message"]["function_call"]
#
#     if function_call:
#         result = function_call["arguments"].split("=")[1].strip()
#         return result == "True"
#     else:
#         return False


# Функция для сохранения ценности в базу данных
# def save_value(telegram_id, value):
#     if validate_value(value):
#         with get_db() as db:
#             user = db.query(User).filter(User.telegram_id == telegram_id).first()
#             if user:
#                 user.values = value
#                 db.commit()
#             else:
#                 new_user = User(telegram_id=telegram_id, values=value)
#                 db.add(new_user)
#                 db.commit()
#         return True
#     else:
#         return False
