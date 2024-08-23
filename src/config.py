from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os
load_dotenv()


class Settings(BaseSettings):
    BOT_TOKEN: str = Field(..., env="BOT_TOKEN")
    OPENAI_API_KEY: str = Field(..., env="OPENAI_API_KEY")

    PGHOST: str = Field(..., env_file="../.env", env="PGHOST", default=os.getenv("RAILWAY_POSTGRESQL_HOST"))
    PGUSER: str = Field(..., env_file="../.env", env="PGUSER", default=os.getenv("RAILWAY_POSTGRESQL_USER"))
    PGPASSWORD: str = Field(..., env_file="../.env", env="PGPASSWORD", default=os.getenv("RAILWAY_POSTGRESQL_PASSWORD"))
    PGDATABASE: str = Field(..., env_file="../.env", env="PGDATABASE", default=os.getenv("RAILWAY_POSTGRESQL_DB_NAME"))
    PGPORT: int = Field(..., env_file="../.env", env="PGPORT",
                        default=int(os.getenv("RAILWAY_POSTGRESQL_PORT", "5432")))


settings = Settings()
