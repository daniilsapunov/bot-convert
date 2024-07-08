import io
import os
from pydub import AudioSegment
from openai import OpenAI, AsyncOpenAI
from aiogram import Bot
from aiogram.types import Voice

from config import settings
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
