from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from src.config import settings

Base = declarative_base()

async_engine = create_async_engine(
    url=settings.database_url_asyncpg, echo=True, pool_pre_ping=True
)

async_session = async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
