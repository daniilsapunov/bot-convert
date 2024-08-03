from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    DB_HOST: str = Field(..., env="DB_HOST")
    DB_USER: str = Field(..., env="DB_USER")
    DB_PASS: str = Field(..., env="DB_PASS")
    DB_NAME: str = Field(..., env="DB_NAME")
    DB_PORT: int = Field(..., env="DB_PORT")

    @property
    def database_url_asyncpg(self):
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'

    class Config:
        env_file = "../.env"


settings = Settings()
