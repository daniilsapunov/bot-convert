from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    PGHOST: str = Field(..., env="PGHOST", env_default=os.getenv("PGHOST"))
    PGUSER: str = Field(..., env="PGUSER", env_default=os.getenv("PGUSER"))
    PGPASSWORD: str = Field(..., env="PGPASSWORD", env_default=os.getenv("RAILWAY_POSTGRESQL_PASSWORD"))
    PGDATABASE: str = Field(..., env="PGDATABASE", env_default=os.getenv("RAILWAY_POSTGRESQL_DB_NAME"))
    PGPORT: int = Field(..., env="PGPORT", env_default=os.getenv("RAILWAY_POSTGRESQL_PORT", "5432"))

    @property
    def database_url_asyncpg(self):
        return f'postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}'

    class Config:
        env_file = "../.env"


settings = Settings()
