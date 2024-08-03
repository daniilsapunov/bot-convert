from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker, Mapped, mapped_column
from src.config import settings

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(unique=True)
    values: Mapped[str]


async_engine = create_async_engine(
    url=settings.database_url_asyncpg, echo=True, pool_pre_ping=True
)

async_session = sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)
