from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")
    PGHOST: str = Field(..., env="PGHOST")
    PGUSER: str = Field(..., env="PGUSER")
    PGPASSWORD: str = Field(..., env="PGPASSWORD")
    PGDATABASE: str = Field(..., env="PGDATABASE")
    PGPORT: int = Field(..., env="PGPORT")

    @property
    def database_url_asyncpg(self):
        return f'postgresql+asyncpg://{self.PGUSER}:{self.PGPASSWORD}@{self.PGHOST}:{self.PGPORT}/{self.PGDATABASE}'

    class Config:
        env_file = "../.env"


settings = Settings()
