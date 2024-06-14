from pydantic import BaseSettings, Field
from dotenv import load_dotenv
import os

load_dotenv() # Загрузите .env перед инициализацией настроек

class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    class Config:
        env_file = ".env"

settings = Settings()