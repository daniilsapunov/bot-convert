from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column
from src.config import settings

Base = declarative_base()

async_engine = create_async_engine(
    url=settings.database_url_asyncpg, echo=True, pool_pre_ping=True
)

async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
